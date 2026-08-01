from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import (
    AssistanceStatus,
    Booking,
    BookingSource,
    BookingStatus,
    BookingVisitor,
    Notification,
    SeniorSathiRequest,
    Temple,
    TimeSlot,
    User,
    UserRole,
)
from app.schemas import BookingCreate, BookingOut, KioskBookingCreate

router = APIRouter(prefix="/bookings", tags=["bookings"])


def make_qr_svg(ticket_code: str) -> str:
    image = qrcode.make(ticket_code, image_factory=qrcode.image.svg.SvgPathImage)
    stream = BytesIO()
    image.save(stream)
    return stream.getvalue().decode("utf-8")


def make_ticket_code(temple: Temple) -> str:
    code = temple.temple_code or "".join(
        char for char in temple.name.upper() if char.isalnum()
    )[:3]

    if not code:
        code = "DD"

    return f"{code}-{uuid4().hex[:10].upper()}"


def serialize_booking(booking: Booking, include_qr: bool = True) -> dict:
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "temple_id": booking.temple_id,
        "slot_id": booking.slot_id,
        "ticket_code": booking.ticket_code,
        "source": booking.source,
        "visit_purpose": booking.visit_purpose,
        "primary_name": booking.primary_name,
        "primary_age": booking.primary_age,
        "primary_gender": booking.primary_gender,
        "primary_phone": booking.primary_phone,
        "primary_email": booking.primary_email,
        "city": booking.city,
        "state": booking.state,
        "visitor_count": booking.visitor_count,
        "senior_count": booking.senior_count,
        "differently_abled_count": booking.differently_abled_count,
        "arrival_mode": booking.arrival_mode,
        "expected_duration_minutes": booking.expected_duration_minutes,
        "preferred_language": booking.preferred_language,
        "needs_assistance": booking.needs_assistance,
        "family_contact_name": booking.family_contact_name,
        "family_contact_phone": booking.family_contact_phone,
        "is_vip": booking.is_vip,
        "vip_reference": booking.vip_reference,
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
        "visitors": booking.visitors or [],
    }


def validate_booking_payload(payload: BookingCreate):
    if payload.senior_count + payload.differently_abled_count > payload.visitor_count:
        raise HTTPException(
            status_code=400,
            detail="Senior and differently-abled count cannot exceed total visitors.",
        )

    if payload.visitors and len(payload.visitors) > payload.visitor_count:
        raise HTTPException(
            status_code=400,
            detail="Visitor detail count cannot exceed total visitor count.",
        )


def get_slot_or_404(db: Session, temple_id: int, slot_id: int) -> tuple[Temple, TimeSlot]:
    temple = db.get(Temple, temple_id)
    slot = db.get(TimeSlot, slot_id)

    if not temple or not slot or slot.temple_id != temple_id:
        raise HTTPException(status_code=404, detail="Temple or slot not found")

    if not temple.is_active:
        raise HTTPException(status_code=400, detail="Temple is not active")

    if not slot.is_active:
        raise HTTPException(status_code=400, detail="Slot is not active")

    if slot.is_vip_blocked:
        raise HTTPException(
            status_code=400,
            detail="This slot is temporarily blocked due to VIP/security movement.",
        )

    slot_end = slot.end_time

    if slot_end.tzinfo is not None:
        now = datetime.now(timezone.utc)
    else:
        now = datetime.now()

    if slot_end < now:
        raise HTTPException(status_code=400, detail="Cannot book an expired slot")

    return temple, slot


def create_booking_record(
    db: Session,
    *,
    payload: BookingCreate,
    current_user: User | None,
    source: BookingSource,
) -> Booking:
    validate_booking_payload(payload)

    temple, slot = get_slot_or_404(db, payload.temple_id, payload.slot_id)

    requested = payload.visitor_count
    available = slot.capacity - slot.booked_count

    if requested > available:
        raise HTTPException(status_code=400, detail=f"Only {available} seats available")

    if payload.senior_count > 0:
        senior_available = slot.senior_reserved_capacity - slot.senior_booked_count
        if payload.senior_count > senior_available:
            raise HTTPException(
                status_code=400,
                detail=f"Only {senior_available} SeniorSathi reserved seats available in this slot.",
            )

    gate_index = slot.booked_count % max(temple.entry_gates, 1)
    gate = "SeniorSathi Gate" if payload.needs_assistance else f"Gate {chr(65 + gate_index)}"

    ticket_code = make_ticket_code(temple)

    booking = Booking(
        user_id=current_user.id if current_user and source == BookingSource.online else None,
        temple_id=temple.id,
        slot_id=slot.id,
        ticket_code=ticket_code,
        source=source,
        visit_purpose=payload.visit_purpose,
        primary_name=payload.primary_name or (current_user.name if current_user else "Walk-in Pilgrim"),
        primary_age=payload.primary_age,
        primary_gender=payload.primary_gender,
        primary_phone=payload.primary_phone or (current_user.phone if current_user else None),
        primary_email=payload.primary_email or (current_user.email if current_user else None),
        city=payload.city,
        state=payload.state,
        visitor_count=payload.visitor_count,
        senior_count=payload.senior_count,
        differently_abled_count=payload.differently_abled_count,
        arrival_mode=payload.arrival_mode,
        expected_duration_minutes=payload.expected_duration_minutes,
        preferred_language=payload.preferred_language,
        needs_assistance=payload.needs_assistance,
        family_contact_name=payload.family_contact_name,
        family_contact_phone=payload.family_contact_phone,
        is_vip=payload.is_vip,
        vip_reference=payload.vip_reference,
        gate=gate,
        ticket_sent_to=payload.primary_phone or payload.primary_email,
        booking_notes=payload.booking_notes,
        created_by_id=current_user.id if current_user else None,
    )

    slot.booked_count += requested
    slot.senior_booked_count += payload.senior_count

    db.add(booking)
    db.flush()

    if payload.visitors:
        for visitor in payload.visitors:
            db.add(
                BookingVisitor(
                    booking_id=booking.id,
                    full_name=visitor.full_name,
                    age=visitor.age,
                    gender=visitor.gender,
                    phone=visitor.phone,
                    is_senior=visitor.is_senior,
                    is_differently_abled=visitor.is_differently_abled,
                    needs_wheelchair=visitor.needs_wheelchair,
                    id_type=visitor.id_type,
                    id_last4=visitor.id_last4,
                )
            )
    else:
        db.add(
            BookingVisitor(
                booking_id=booking.id,
                full_name=booking.primary_name,
                age=booking.primary_age,
                gender=booking.primary_gender,
                phone=booking.primary_phone,
                is_senior=payload.senior_count > 0,
                is_differently_abled=payload.differently_abled_count > 0,
                needs_wheelchair=payload.needs_assistance,
            )
        )

    if payload.needs_assistance or payload.senior_count > 0 or payload.differently_abled_count > 0:
        db.add(
            SeniorSathiRequest(
                booking_id=booking.id,
                temple_id=temple.id,
                status=AssistanceStatus.pending,
                family_contact_name=payload.family_contact_name,
                family_contact_phone=payload.family_contact_phone,
                priority_gate="SeniorSathi Gate",
                notes="Auto-created from booking request.",
            )
        )

    if current_user and booking.user_id:
        db.add(
            Notification(
                user_id=current_user.id,
                temple_id=temple.id,
                title="Digii-Darshan ticket confirmed",
                message=f"Your ticket {ticket_code} is confirmed for {temple.name}.",
            )
        )

    db.commit()

    booking = (
        db.query(Booking)
        .options(
            joinedload(Booking.temple),
            joinedload(Booking.slot),
            joinedload(Booking.visitors),
        )
        .filter(Booking.id == booking.id)
        .first()
    )

    return booking


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = create_booking_record(
        db,
        payload=payload,
        current_user=current_user,
        source=BookingSource.online,
    )

    return serialize_booking(booking)


@router.post("/kiosk", response_model=BookingOut, status_code=201)
def create_kiosk_booking(
    payload: KioskBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.super_admin,
            UserRole.temple_admin,
            UserRole.kiosk_operator,
        )
    ),
):
    booking = create_booking_record(
        db,
        payload=payload,
        current_user=current_user,
        source=payload.source,
    )

    return serialize_booking(booking)


@router.get("/me", response_model=list[BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = (
        db.query(Booking)
        .options(
            joinedload(Booking.temple),
            joinedload(Booking.slot),
            joinedload(Booking.visitors),
        )
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    return [serialize_booking(booking) for booking in bookings]


@router.get("", response_model=list[BookingOut])
def all_bookings(
    temple_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_roles(
            UserRole.admin,
            UserRole.super_admin,
            UserRole.temple_admin,
            UserRole.scanner,
            UserRole.emergency_operator,
            UserRole.kiosk_operator,
        )
    ),
):
    query = (
        db.query(Booking)
        .options(
            joinedload(Booking.temple),
            joinedload(Booking.slot),
            joinedload(Booking.visitors),
        )
        .order_by(Booking.created_at.desc())
    )

    if temple_id:
        query = query.filter(Booking.temple_id == temple_id)

    bookings = query.limit(300).all()

    return [serialize_booking(booking, include_qr=False) for booking in bookings]


@router.get("/{booking_id}", response_model=BookingOut)
def booking_detail(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .options(
            joinedload(Booking.temple),
            joinedload(Booking.slot),
            joinedload(Booking.visitors),
        )
        .filter(Booking.id == booking_id)
        .first()
    )

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role == UserRole.pilgrim and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access this booking")

    return serialize_booking(booking)


@router.delete("/{booking_id}", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .options(
            joinedload(Booking.temple),
            joinedload(Booking.slot),
            joinedload(Booking.visitors),
        )
        .filter(Booking.id == booking_id)
        .first()
    )

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.id and current_user.role not in [
        UserRole.admin,
        UserRole.super_admin,
        UserRole.temple_admin,
    ]:
        raise HTTPException(status_code=403, detail="Cannot cancel this booking")

    if booking.status != BookingStatus.booked:
        raise HTTPException(status_code=400, detail="Only booked tickets can be cancelled")

    booking.status = BookingStatus.cancelled

    booking.slot.booked_count = max(
        booking.slot.booked_count - booking.visitor_count,
        0,
    )

    booking.slot.senior_booked_count = max(
        booking.slot.senior_booked_count - booking.senior_count,
        0,
    )

    db.commit()
    db.refresh(booking)

    return serialize_booking(booking)