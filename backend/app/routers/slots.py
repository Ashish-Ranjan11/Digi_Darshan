from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import require_roles
from app.models import Temple, TimeSlot, User, UserRole
from app.schemas import TimeSlotCreate
from app.services.slot_engine import (
    generate_daily_slots_for_all_temples,
    generate_daily_slots_for_temple,
)

router = APIRouter(prefix="/slots", tags=["slots"])


def serialize_slot(slot: TimeSlot) -> dict:
    available = max((slot.capacity or 0) - (slot.booked_count or 0), 0)

    return {
        "id": slot.id,
        "temple_id": slot.temple_id,
        "temple_name": slot.temple.name if getattr(slot, "temple", None) else None,
        "start_time": slot.start_time,
        "end_time": slot.end_time,
        "capacity": slot.capacity,
        "booked_count": slot.booked_count,
        "senior_reserved_capacity": slot.senior_reserved_capacity,
        "senior_booked_count": 0,
        "is_active": slot.is_active,
        "available_count": available,
        "available_capacity": available,
    }


@router.get("")
def list_slots(
    temple_id: int | None = Query(default=None),
    upcoming_only: bool = True,
    db: Session = Depends(get_db),
):
    query = (
        db.query(TimeSlot)
        .options(joinedload(TimeSlot.temple))
        .filter(TimeSlot.is_active.is_(True))
    )

    if temple_id:
        temple = db.get(Temple, temple_id)
        if not temple:
            raise HTTPException(status_code=404, detail="Temple not found")

        generate_daily_slots_for_temple(
            db=db,
            temple_id=temple_id,
            days_ahead=7,
            start_hour=6,
            end_hour=18,
            capacity=300,
            senior_reserved_capacity=40,
        )

        query = query.filter(TimeSlot.temple_id == temple_id)

    if upcoming_only:
        query = query.filter(TimeSlot.end_time >= datetime.now())

    slots = query.order_by(TimeSlot.start_time.asc()).limit(120).all()
    return [serialize_slot(slot) for slot in slots]


@router.get("/temple/{temple_id}")
def get_slots_for_temple(temple_id: int, db: Session = Depends(get_db)):
    temple = db.get(Temple, temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    generate_daily_slots_for_temple(
        db=db,
        temple_id=temple_id,
        days_ahead=7,
        start_hour=6,
        end_hour=18,
        capacity=300,
        senior_reserved_capacity=40,
    )

    slots = (
        db.query(TimeSlot)
        .options(joinedload(TimeSlot.temple))
        .filter(TimeSlot.temple_id == temple_id)
        .filter(TimeSlot.is_active.is_(True))
        .filter(TimeSlot.end_time >= datetime.now())
        .order_by(TimeSlot.start_time.asc())
        .limit(84)
        .all()
    )

    return [serialize_slot(slot) for slot in slots]


@router.post("", status_code=201)
def create_slot(
    payload: TimeSlotCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temple = db.get(Temple, payload.temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    slot = TimeSlot(
        temple_id=payload.temple_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        capacity=payload.capacity,
        booked_count=0,
        senior_reserved_capacity=payload.senior_reserved_capacity,
        is_active=True,
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)

    return serialize_slot(slot)


@router.patch("/{slot_id}/toggle")
def toggle_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    slot = db.get(TimeSlot, slot_id)

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    slot.is_active = not slot.is_active
    db.commit()
    db.refresh(slot)

    return serialize_slot(slot)


@router.post("/auto-generate", status_code=201)
def auto_generate_all_slots(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    created = generate_daily_slots_for_all_temples(
        db=db,
        days_ahead=7,
        capacity=300,
    )

    return {
        "message": "Automatic slots generated successfully.",
        "slots_created": created,
        "rules": "6 AM to 6 PM, 1-hour slots, 300 capacity per slot, for every temple.",
    }