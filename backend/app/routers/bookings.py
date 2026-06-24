from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import Booking, BookingStatus, Temple, TimeSlot, User, UserRole
from app.schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/bookings", tags=["bookings"])


def make_qr_svg(ticket_code: str) -> str:
    image = qrcode.make(ticket_code, image_factory=qrcode.image.svg.SvgPathImage)
    stream = BytesIO()
    image.save(stream)
    return stream.getvalue().decode("utf-8")


def serialize_booking(booking: Booking, include_qr: bool = True) -> dict:
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "temple_id": booking.temple_id,
        "slot_id": booking.slot_id,
        "ticket_code": booking.ticket_code,
        "visitor_count": booking.visitor_count,
        "senior_count": booking.senior_count,
        "differently_abled_count": booking.differently_abled_count,
        "status": booking.status,
        "gate": booking.gate,
        "created_at": booking.created_at,
        "checked_in_at": booking.checked_in_at,
        "checked_out_at": booking.checked_out_at,
        "temple_name": booking.temple.name if booking.temple else None,
        "temple_city": booking.temple.city if booking.temple else None,
        "slot_start": booking.slot.start_time if booking.slot else None,
        "slot_end": booking.slot.end_time if booking.slot else None,
        "qr_svg": make_qr_svg(booking.ticket_code) if include_qr else None,
    }


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    temple = db.get(Temple, payload.temple_id)
    slot = db.get(TimeSlot, payload.slot_id)
    if not temple or not slot or slot.temple_id != payload.temple_id:
        raise HTTPException(status_code=404, detail="Temple or slot not found")
    if not slot.is_active:
        raise HTTPException(status_code=400, detail="Slot is not active")
    slot_end = slot.end_time
    if slot_end.tzinfo is None:
        slot_end = slot_end.replace(tzinfo=timezone.utc)
    if slot_end < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Cannot book an expired slot")
    requested = payload.visitor_count
    available = slot.capacity - slot.booked_count
    if requested > available:
        raise HTTPException(status_code=400, detail=f"Only {available} seats available")

    gate_index = slot.booked_count % max(temple.entry_gates, 1)
    booking = Booking(
        user_id=current_user.id,
        temple_id=temple.id,
        slot_id=slot.id,
        ticket_code=f"DD-{uuid4().hex[:10].upper()}",
        visitor_count=payload.visitor_count,
        senior_count=payload.senior_count,
        differently_abled_count=payload.differently_abled_count,
        gate=f"Gate {chr(65 + gate_index)}",
    )
    slot.booked_count += requested
    db.add(booking)
    db.commit()
    db.refresh(booking)
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.temple), joinedload(Booking.slot))
        .filter(Booking.id == booking.id)
        .first()
    )
    return serialize_booking(booking)


@router.get("/me", response_model=list[BookingOut])
def my_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.temple), joinedload(Booking.slot))
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return [serialize_booking(booking) for booking in bookings]


@router.get("", response_model=list[BookingOut])
def all_bookings(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.scanner, UserRole.emergency_operator)),
):
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.temple), joinedload(Booking.slot))
        .order_by(Booking.created_at.desc())
        .limit(200)
        .all()
    )
    return [serialize_booking(booking, include_qr=False) for booking in bookings]


@router.delete("/{booking_id}", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.temple), joinedload(Booking.slot))
        .filter(Booking.id == booking_id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Cannot cancel this booking")
    if booking.status != BookingStatus.booked:
        raise HTTPException(status_code=400, detail="Only booked tickets can be cancelled")
    booking.status = BookingStatus.cancelled
    booking.slot.booked_count = max(booking.slot.booked_count - booking.visitor_count, 0)
    db.commit()
    db.refresh(booking)
    return serialize_booking(booking)
