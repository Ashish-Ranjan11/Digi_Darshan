from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import Temple, TimeSlot, User, UserRole
from app.schemas import TimeSlotCreate, TimeSlotOut

router = APIRouter(prefix="/slots", tags=["slots"])


def serialize_slot(slot: TimeSlot) -> dict:
    return {
        "id": slot.id,
        "temple_id": slot.temple_id,
        "start_time": slot.start_time,
        "end_time": slot.end_time,
        "capacity": slot.capacity,
        "booked_count": slot.booked_count,
        "senior_reserved_capacity": slot.senior_reserved_capacity,
        "is_active": slot.is_active,
        "available_count": max(slot.capacity - slot.booked_count, 0),
    }


@router.get("", response_model=list[TimeSlotOut])
def list_slots(
    temple_id: int | None = Query(default=None),
    upcoming_only: bool = True,
    db: Session = Depends(get_db),
):
    query = db.query(TimeSlot).filter(TimeSlot.is_active.is_(True))
    if temple_id:
        query = query.filter(TimeSlot.temple_id == temple_id)
    if upcoming_only:
        query = query.filter(TimeSlot.end_time >= datetime.now(timezone.utc))
    slots = query.order_by(TimeSlot.start_time).limit(80).all()
    return [serialize_slot(slot) for slot in slots]


@router.post("", response_model=TimeSlotOut, status_code=201)
def create_slot(
    payload: TimeSlotCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    temple = db.get(Temple, payload.temple_id)
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    slot = TimeSlot(**payload.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return serialize_slot(slot)


@router.patch("/{slot_id}/toggle", response_model=TimeSlotOut)
def toggle_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    slot = db.get(TimeSlot, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    slot.is_active = not slot.is_active
    db.commit()
    db.refresh(slot)
    return serialize_slot(slot)
