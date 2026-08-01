from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Booking,
    BookingStatus,
    CrowdReading,
    GateEvent,
    ScannerLog,
    Temple,
    User,
)
from app.routers.bookings import serialize_booking
from app.routers.temples import crowd_level
from app.services.crowd_engine import build_live_payload


def normalize_ticket(ticket_code: str) -> str:
    return ticket_code.strip().upper()


def calculate_density(temple: Temple) -> float:
    if not temple.max_capacity:
        return 0.0

    return round(min((temple.current_occupancy / temple.max_capacity), 1), 2)


def create_scan_log(
    db: Session,
    *,
    ticket_code: str,
    action: str,
    gate: str,
    status: str,
    message: str,
    current_user: User,
    booking: Booking | None = None,
    temple_id: int | None = None,
) -> ScannerLog:
    log = ScannerLog(
        booking_id=booking.id if booking else None,
        temple_id=temple_id or (booking.temple_id if booking else None),
        ticket_code=ticket_code,
        action=action,
        gate=gate,
        status=status,
        message=message,
        scanned_by_id=current_user.id,
    )

    db.add(log)
    return log


def raise_scan_error(
    db: Session,
    *,
    status_code: int,
    detail: str,
    ticket_code: str,
    action: str,
    gate: str,
    current_user: User,
    booking: Booking | None = None,
):
    create_scan_log(
        db,
        ticket_code=ticket_code,
        action=action,
        gate=gate,
        status="failed",
        message=detail,
        current_user=current_user,
        booking=booking,
    )

    db.commit()

    raise HTTPException(status_code=status_code, detail=detail)


def get_booking_by_ticket(db: Session, ticket_code: str) -> Booking | None:
    return (
        db.query(Booking)
        .options(joinedload(Booking.temple), joinedload(Booking.slot))
        .filter(Booking.ticket_code == ticket_code)
        .first()
    )


def verify_booking_status(
    booking: Booking,
    *,
    action: str,
    db: Session,
    ticket_code: str,
    gate: str,
    current_user: User,
):
    if action == "check-in":
        if booking.status != BookingStatus.booked:
            raise_scan_error(
                db,
                status_code=400,
                detail=f"Ticket cannot be checked in because it is already {booking.status.value}.",
                ticket_code=ticket_code,
                action=action,
                gate=gate,
                current_user=current_user,
                booking=booking,
            )

        slot_end = booking.slot.end_time

        if slot_end.tzinfo is None:
            slot_end = slot_end.replace(tzinfo=timezone.utc)

        if slot_end < datetime.now(timezone.utc):
            raise_scan_error(
                db,
                status_code=400,
                detail="Ticket slot has expired. Check-in is not allowed.",
                ticket_code=ticket_code,
                action=action,
                gate=gate,
                current_user=current_user,
                booking=booking,
            )

    if action == "check-out":
        if booking.status != BookingStatus.checked_in:
            raise_scan_error(
                db,
                status_code=400,
                detail="Ticket must be checked in before check-out.",
                ticket_code=ticket_code,
                action=action,
                gate=gate,
                current_user=current_user,
                booking=booking,
            )


def build_scanner_response(
    *,
    booking: Booking,
    action: str,
    gate: str,
    message: str,
    scan_log: ScannerLog,
    live_payload: dict,
) -> dict:
    return {
        "success": True,
        "action": action,
        "message": message,
        "gate": gate,
        "scanner_log_id": scan_log.id,
        "temple_id": booking.temple_id,
        "temple_name": booking.temple.name if booking.temple else None,
        "booking": serialize_booking(booking, include_qr=False),
        "live_crowd": live_payload,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def process_gate_scan(
    db: Session,
    *,
    ticket_code: str,
    gate: str,
    action: str,
    current_user: User,
) -> tuple[dict, dict]:
    clean_ticket = normalize_ticket(ticket_code)

    if action not in ["check-in", "check-out"]:
        raise HTTPException(status_code=400, detail="Invalid scanner action")

    booking = get_booking_by_ticket(db, clean_ticket)

    if not booking:
        raise_scan_error(
            db,
            status_code=404,
            detail="Ticket not found.",
            ticket_code=clean_ticket,
            action=action,
            gate=gate,
            current_user=current_user,
        )

    verify_booking_status(
        booking,
        action=action,
        db=db,
        ticket_code=clean_ticket,
        gate=gate,
        current_user=current_user,
    )

    temple: Temple = booking.temple
    now = datetime.now(timezone.utc)

    if action == "check-in":
        booking.status = BookingStatus.checked_in
        booking.checked_in_at = now
        booking.gate = gate

        temple.current_occupancy = min(
            temple.current_occupancy + booking.visitor_count,
            temple.max_capacity,
        )

        inflow = booking.visitor_count
        outflow = 0
        event_type = "check_in"
        message = "Check-in successful. Pilgrim entry recorded."

    else:
        booking.status = BookingStatus.completed
        booking.checked_out_at = now

        temple.current_occupancy = max(
            temple.current_occupancy - booking.visitor_count,
            0,
        )

        inflow = 0
        outflow = booking.visitor_count
        event_type = "check_out"
        message = "Check-out successful. Pilgrim exit recorded."

    density_score = calculate_density(temple)

    reading = CrowdReading(
        temple_id=temple.id,
        source="gate_scanner",
        occupancy=temple.current_occupancy,
        inflow_per_min=inflow,
        outflow_per_min=outflow,
        density_score=density_score,
        notes=f"{action} via {gate}",
    )

    event = GateEvent(
        temple_id=temple.id,
        booking_id=booking.id,
        gate=gate,
        event_type=event_type,
        visitor_count=booking.visitor_count,
        created_by_id=current_user.id,
    )

    scan_log = create_scan_log(
        db,
        ticket_code=clean_ticket,
        action=action,
        gate=gate,
        status="success",
        message=message,
        current_user=current_user,
        booking=booking,
    )

    db.add(reading)
    db.add(event)
    db.commit()
    db.refresh(booking)
    db.refresh(scan_log)

    booking = get_booking_by_ticket(db, clean_ticket)

    live_payload = build_live_payload(
        temple=temple,
        occupancy=temple.current_occupancy,
        inflow_per_min=inflow,
        outflow_per_min=outflow,
        source="gate_scanner",
        notes=f"{action} scan from {gate}",
    )

    scanner_response = build_scanner_response(
        booking=booking,
        action=action,
        gate=gate,
        message=message,
        scan_log=scan_log,
        live_payload=live_payload,
    )

    websocket_payload = {
        "type": "gate_scan",
        "scan_action": action,
        "ticket_code": booking.ticket_code,
        "gate": gate,
        "visitor_count": booking.visitor_count,
        "occupancy": temple.current_occupancy,
        "occupancy_percent": live_payload["occupancy_percent"],
        "crowd_level": live_payload["crowd_level"],
        "recommendation": live_payload["recommendation"],
        "timestamp": live_payload["timestamp"],
    }

    return scanner_response, websocket_payload


def verify_ticket_only(
    db: Session,
    *,
    ticket_code: str,
    gate: str,
    current_user: User,
) -> dict:
    clean_ticket = normalize_ticket(ticket_code)
    booking = get_booking_by_ticket(db, clean_ticket)

    if not booking:
        create_scan_log(
            db,
            ticket_code=clean_ticket,
            action="verify",
            gate=gate,
            status="failed",
            message="Ticket not found.",
            current_user=current_user,
        )
        db.commit()
        raise HTTPException(status_code=404, detail="Ticket not found.")

    create_scan_log(
        db,
        ticket_code=clean_ticket,
        action="verify",
        gate=gate,
        status="success",
        message="Ticket verified successfully.",
        current_user=current_user,
        booking=booking,
    )

    db.commit()

    percent = (
        round((booking.temple.current_occupancy / booking.temple.max_capacity) * 100, 2)
        if booking.temple and booking.temple.max_capacity
        else 0
    )

    return {
        "success": True,
        "message": "Ticket verified successfully.",
        "ticket_status": booking.status.value,
        "temple_id": booking.temple_id,
        "temple_name": booking.temple.name if booking.temple else None,
        "gate": gate,
        "booking": serialize_booking(booking, include_qr=False),
        "live_crowd": {
            "occupancy": booking.temple.current_occupancy,
            "max_capacity": booking.temple.max_capacity,
            "occupancy_percent": percent,
            "crowd_level": crowd_level(percent),
        },
    }
