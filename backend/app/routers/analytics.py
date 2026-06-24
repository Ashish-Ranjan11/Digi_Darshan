from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import CrowdReading, Temple, User, UserRole
from app.services.analytics_engine import build_realtime_analysis_payload

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/realtime/{temple_id}")
def get_realtime_analysis(
    temple_id: int,
    window_minutes: int = Query(default=30, ge=5, le=240),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temple = db.get(Temple, temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

    readings = (
        db.query(CrowdReading)
        .filter(CrowdReading.temple_id == temple_id)
        .filter(CrowdReading.created_at >= since)
        .order_by(CrowdReading.created_at.asc())
        .all()
    )

    if not readings:
        readings = (
            db.query(CrowdReading)
            .filter(CrowdReading.temple_id == temple_id)
            .order_by(CrowdReading.created_at.desc())
            .limit(30)
            .all()
        )
        readings = list(reversed(readings))

    return build_realtime_analysis_payload(
        temple=temple,
        readings=readings,
        window_minutes=window_minutes,
    )


@router.get("/summary")
def get_system_analytics_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temples = db.query(Temple).all()

    summaries = []

    for temple in temples:
        readings = (
            db.query(CrowdReading)
            .filter(CrowdReading.temple_id == temple.id)
            .order_by(CrowdReading.created_at.desc())
            .limit(20)
            .all()
        )

        readings = list(reversed(readings))

        summaries.append(
            build_realtime_analysis_payload(
                temple=temple,
                readings=readings,
                window_minutes=30,
            )
        )

    critical_temples = [
        item for item in summaries if item["risk_level"] == "critical"
    ]

    high_temples = [
        item for item in summaries if item["risk_level"] == "high"
    ]

    avg_stability = 0

    if summaries:
        avg_stability = round(
            sum(item["system_stability_score"] for item in summaries)
            / len(summaries),
            2,
        )

    return {
        "temples_monitored": len(summaries),
        "critical_temples": len(critical_temples),
        "high_risk_temples": len(high_temples),
        "average_system_stability": avg_stability,
        "temples": summaries,
    }
