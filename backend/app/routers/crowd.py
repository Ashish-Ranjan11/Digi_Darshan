from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import (
    Alert,
    AlertSeverity,
    AlertStatus,
    CrowdReading,
    Temple,
    User,
    UserRole,
)
from app.schemas import CrowdReadingCreate, CrowdReadingOut
from app.services.crowd_engine import build_live_payload, next_simulated_counts
from app.websocket_manager import manager

router = APIRouter(prefix="/crowd", tags=["crowd"])


@router.get("/readings/{temple_id}", response_model=list[CrowdReadingOut])
def get_readings(temple_id: int, db: Session = Depends(get_db)):
    temple = db.get(Temple, temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    return (
        db.query(CrowdReading)
        .filter(CrowdReading.temple_id == temple_id)
        .order_by(CrowdReading.created_at.desc())
        .limit(50)
        .all()
    )


@router.get("/live/{temple_id}")
def get_live_crowd_status(temple_id: int, db: Session = Depends(get_db)):
    temple = db.get(Temple, temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    latest = (
        db.query(CrowdReading)
        .filter(CrowdReading.temple_id == temple_id)
        .order_by(CrowdReading.created_at.desc())
        .first()
    )

    inflow = latest.inflow_per_min if latest else 0
    outflow = latest.outflow_per_min if latest else 0
    source = latest.source if latest else "initial"
    notes = latest.notes if latest else "No live reading yet"

    return build_live_payload(
        temple=temple,
        occupancy=temple.current_occupancy or 0,
        inflow_per_min=inflow,
        outflow_per_min=outflow,
        source=source,
        notes=notes,
    )


@router.post("/readings", response_model=CrowdReadingOut, status_code=201)
async def create_reading(
    payload: CrowdReadingCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temple = db.get(Temple, payload.temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    live_payload = build_live_payload(
        temple=temple,
        occupancy=payload.occupancy,
        inflow_per_min=payload.inflow_per_min,
        outflow_per_min=payload.outflow_per_min,
        source=payload.source,
        notes=payload.notes,
    )

    temple.current_occupancy = live_payload["occupancy"]

    reading = CrowdReading(
        temple_id=payload.temple_id,
        source=payload.source,
        occupancy=live_payload["occupancy"],
        inflow_per_min=payload.inflow_per_min,
        outflow_per_min=payload.outflow_per_min,
        density_score=live_payload["density_score"],
        notes=payload.notes,
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    await manager.broadcast(temple.id, live_payload)

    return reading


@router.post("/simulate/{temple_id}")
async def simulate_live_sensor_reading(
    temple_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temple = db.get(Temple, temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    occupancy, inflow, outflow = next_simulated_counts(temple)

    live_payload = build_live_payload(
        temple=temple,
        occupancy=occupancy,
        inflow_per_min=inflow,
        outflow_per_min=outflow,
        source="sensor-simulation",
        notes="Simulated sensor reading for real-time demo",
    )

    temple.current_occupancy = live_payload["occupancy"]

    reading = CrowdReading(
        temple_id=temple.id,
        source="sensor-simulation",
        occupancy=live_payload["occupancy"],
        inflow_per_min=live_payload["inflow_per_min"],
        outflow_per_min=live_payload["outflow_per_min"],
        density_score=live_payload["density_score"],
        notes=live_payload["notes"],
    )

    db.add(reading)

    if live_payload["crowd_level"] in ["high", "critical"]:
        severity = (
            AlertSeverity.critical
            if live_payload["crowd_level"] == "critical"
            else AlertSeverity.warning
        )

        existing_active_alert = (
            db.query(Alert)
            .filter(
                Alert.temple_id == temple.id,
                Alert.status == AlertStatus.active,
                Alert.severity == severity,
            )
            .first()
        )

        if not existing_active_alert:
            db.add(
                Alert(
                    temple_id=temple.id,
                    title=f"{live_payload['crowd_level'].title()} crowd density detected",
                    message=(
                        f"{temple.name} occupancy is now "
                        f"{live_payload['occupancy_percent']}% with "
                        f"{live_payload['trend'].replace('_', ' ')} movement."
                    ),
                    severity=severity,
                    location="Main queue corridor",
                    instruction=live_payload["recommendation"],
                )
            )

    db.commit()
    db.refresh(reading)

    await manager.broadcast(temple.id, live_payload)

    return live_payload