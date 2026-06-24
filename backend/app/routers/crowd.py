from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import CrowdReading, Temple, User, UserRole
from app.routers.temples import crowd_level
from app.schemas import CrowdReadingCreate, CrowdReadingOut
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


@router.post("/readings", response_model=CrowdReadingOut, status_code=201)
async def create_reading(
    payload: CrowdReadingCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temple = db.get(Temple, payload.temple_id)
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")
    reading = CrowdReading(**payload.model_dump())
    temple.current_occupancy = min(payload.occupancy, temple.max_capacity)
    db.add(reading)
    db.commit()
    db.refresh(reading)

    percent = round((temple.current_occupancy / temple.max_capacity) * 100, 2) if temple.max_capacity else 0
    await manager.broadcast(
        temple.id,
        {
            "type": "crowd_update",
            "temple_id": temple.id,
            "occupancy": temple.current_occupancy,
            "occupancy_percent": percent,
            "crowd_level": crowd_level(percent),
            "message": f"{temple.name} crowd level is {crowd_level(percent)}",
        },
    )
    return reading
