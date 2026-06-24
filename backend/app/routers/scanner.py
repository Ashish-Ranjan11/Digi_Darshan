from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import require_roles
from app.models import Booking, BookingStatus, CrowdReading, Temple, User, UserRole
from app.routers.bookings import serialize_booking
from app.routers.temples import crowd_level
from app.schemas import BookingOut, ScannerRequest
from app.websocket_manager import manager

router = APIRouter(prefix="/scanner", tags=["scanner"])


@router.post("/check-in", response_model=BookingOut)
async def check_in(
    payload: ScannerRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.scanner)),
):
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.temple), joinedload(Booking.slot))
        .filter(Booking.ticket_code == payload.ticket_code.strip().upper())
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if booking.status != BookingStatus.booked:
        raise HTTPException(status_code=400, detail=f"Ticket is already {booking.status.value}")

    booking.status = BookingStatus.checked_in
    booking.checked_in_at = datetime.now(timezone.utc)
    booking.gate = payload.gate
    temple: Temple = booking.temple
    temple.current_occupancy = min(temple.current_occupancy + booking.visitor_count, temple.max_capacity)
    db.add(CrowdReading(temple_id=temple.id, source="scanner", occupancy=temple.current_occupancy, notes="Check-in scan"))
    db.commit()
    db.refresh(booking)

    percent = round((temple.current_occupancy / temple.max_capacity) * 100, 2) if temple.max_capacity else 0
    await manager.broadcast(
        temple.id,
        {
            "type": "check_in",
            "ticket_code": booking.ticket_code,
            "occupancy": temple.current_occupancy,
            "occupancy_percent": percent,
            "crowd_level": crowd_level(percent),
        },
    )
    return serialize_booking(booking)


@router.post("/check-out", response_model=BookingOut)
async def check_out(
    payload: ScannerRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.scanner)),
):
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.temple), joinedload(Booking.slot))
        .filter(Booking.ticket_code == payload.ticket_code.strip().upper())
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if booking.status != BookingStatus.checked_in:
        raise HTTPException(status_code=400, detail="Ticket must be checked-in before check-out")

    booking.status = BookingStatus.completed
    booking.checked_out_at = datetime.now(timezone.utc)
    temple: Temple = booking.temple
    temple.current_occupancy = max(temple.current_occupancy - booking.visitor_count, 0)
    db.add(CrowdReading(temple_id=temple.id, source="scanner", occupancy=temple.current_occupancy, notes="Check-out scan"))
    db.commit()
    db.refresh(booking)

    percent = round((temple.current_occupancy / temple.max_capacity) * 100, 2) if temple.max_capacity else 0
    await manager.broadcast(
        temple.id,
        {
            "type": "check_out",
            "ticket_code": booking.ticket_code,
            "occupancy": temple.current_occupancy,
            "occupancy_percent": percent,
            "crowd_level": crowd_level(percent),
        },
    )
    return serialize_booking(booking)
