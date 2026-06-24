from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import Temple, User, UserRole
from app.schemas import TempleCreate, TempleOut

router = APIRouter(prefix="/temples", tags=["temples"])


def crowd_level(percent: float) -> str:
    if percent >= 90:
        return "critical"
    if percent >= 70:
        return "high"
    if percent >= 45:
        return "medium"
    return "low"


def serialize_temple(temple: Temple) -> dict:
    percent = round((temple.current_occupancy / temple.max_capacity) * 100, 2) if temple.max_capacity else 0
    return {
        "id": temple.id,
        "name": temple.name,
        "city": temple.city,
        "description": temple.description,
        "latitude": temple.latitude,
        "longitude": temple.longitude,
        "max_capacity": temple.max_capacity,
        "current_occupancy": temple.current_occupancy,
        "entry_gates": temple.entry_gates,
        "exit_gates": temple.exit_gates,
        "emergency_contact": temple.emergency_contact,
        "is_active": temple.is_active,
        "occupancy_percent": percent,
        "crowd_level": crowd_level(percent),
    }


@router.get("", response_model=list[TempleOut])
def list_temples(db: Session = Depends(get_db)):
    temples = db.query(Temple).filter(Temple.is_active.is_(True)).order_by(Temple.name).all()
    return [serialize_temple(temple) for temple in temples]


@router.get("/{temple_id}", response_model=TempleOut)
def get_temple(temple_id: int, db: Session = Depends(get_db)):
    temple = db.get(Temple, temple_id)
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")
    return serialize_temple(temple)


@router.post("", response_model=TempleOut, status_code=201)
def create_temple(
    payload: TempleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    temple = Temple(**payload.model_dump())
    db.add(temple)
    db.commit()
    db.refresh(temple)
    return serialize_temple(temple)


@router.put("/{temple_id}", response_model=TempleOut)
def update_temple(
    temple_id: int,
    payload: TempleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    temple = db.get(Temple, temple_id)
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")
    for key, value in payload.model_dump().items():
        setattr(temple, key, value)
    db.commit()
    db.refresh(temple)
    return serialize_temple(temple)
