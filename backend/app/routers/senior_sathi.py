from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import (
    AssistanceStatus,
    Booking,
    SeniorSathiRequest,
    Temple,
    User,
    UserRole,
)

router = APIRouter(prefix="/senior-sathi", tags=["SeniorSathi"])


def enum_value(value):
    if hasattr(value, "value"):
        return value.value
    return value


def serialize_request(item: SeniorSathiRequest, db: Session):
    booking = db.get(Booking, item.booking_id) if item.booking_id else None
    temple = db.get(Temple, item.temple_id) if item.temple_id else None
    volunteer = (
        db.get(User, item.assigned_volunteer_id)
        if item.assigned_volunteer_id
        else None
    )

    return {
        "id": item.id,
        "booking_id": item.booking_id,
        "temple_id": item.temple_id,
        "temple_name": temple.name if temple else None,
        "temple_city": temple.city if temple else None,
        "assistance_type": item.assistance_type,
        "status": enum_value(item.status),
        "assigned_volunteer_id": item.assigned_volunteer_id,
        "assigned_volunteer_name": volunteer.name if volunteer else None,
        "family_contact_name": item.family_contact_name,
        "family_contact_phone": item.family_contact_phone,
        "priority_gate": item.priority_gate,
        "notes": item.notes,
        "created_at": item.created_at,
        "assigned_at": item.assigned_at,
        "completed_at": item.completed_at,
        "pilgrim_name": booking.primary_name if booking else None,
        "pilgrim_phone": booking.primary_phone if booking else None,
        "primary_age": booking.primary_age if booking else None,
        "primary_gender": booking.primary_gender if booking else None,
        "visitor_count": booking.visitor_count if booking else 0,
        "senior_count": booking.senior_count if booking else 0,
        "differently_abled_count": booking.differently_abled_count if booking else 0,
        "ticket_code": booking.ticket_code if booking else None,
        "visit_purpose": enum_value(booking.visit_purpose) if booking else None,
        "slot_id": booking.slot_id if booking else None,
        "gate": booking.gate if booking else None,
    }


def allowed_user():
    return require_roles(
        UserRole.senior_sathi_volunteer,
        UserRole.admin,
        UserRole.super_admin,
        UserRole.temple_admin,
        UserRole.emergency_operator,
    )


@router.get("/summary")
def senior_sathi_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_user()),
):
    pending = (
        db.query(SeniorSathiRequest)
        .filter(SeniorSathiRequest.status == AssistanceStatus.pending)
        .count()
    )

    assigned = (
        db.query(SeniorSathiRequest)
        .filter(SeniorSathiRequest.status == AssistanceStatus.assigned)
        .count()
    )

    completed = (
        db.query(SeniorSathiRequest)
        .filter(SeniorSathiRequest.status == AssistanceStatus.completed)
        .count()
    )

    my_assigned = (
        db.query(SeniorSathiRequest)
        .filter(SeniorSathiRequest.assigned_volunteer_id == current_user.id)
        .filter(SeniorSathiRequest.status == AssistanceStatus.assigned)
        .count()
    )

    return {
        "pending": pending,
        "assigned": assigned,
        "completed": completed,
        "my_assigned": my_assigned,
    }


@router.get("/requests")
def list_senior_sathi_requests(
    status: str = Query("open"),
    temple_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_user()),
):
    query = db.query(SeniorSathiRequest).order_by(
        SeniorSathiRequest.created_at.desc()
    )

    if temple_id:
        query = query.filter(SeniorSathiRequest.temple_id == temple_id)

    if status == "open":
        query = query.filter(
            SeniorSathiRequest.status.in_(
                [AssistanceStatus.pending, AssistanceStatus.assigned]
            )
        )
    elif status != "all":
        try:
            status_enum = AssistanceStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

        query = query.filter(SeniorSathiRequest.status == status_enum)

    requests = query.all()

    return [serialize_request(item, db) for item in requests]


@router.post("/requests/{request_id}/assign")
def assign_senior_sathi_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_user()),
):
    item = db.get(SeniorSathiRequest, request_id)

    if not item:
        raise HTTPException(status_code=404, detail="SeniorSathi request not found")

    if item.status == AssistanceStatus.completed:
        raise HTTPException(status_code=400, detail="Request already completed")

    item.status = AssistanceStatus.assigned
    item.assigned_volunteer_id = current_user.id
    item.assigned_at = datetime.utcnow()

    if not item.priority_gate:
        item.priority_gate = "SeniorSathi Gate"

    db.commit()
    db.refresh(item)

    return serialize_request(item, db)


@router.post("/requests/{request_id}/complete")
def complete_senior_sathi_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_user()),
):
    item = db.get(SeniorSathiRequest, request_id)

    if not item:
        raise HTTPException(status_code=404, detail="SeniorSathi request not found")

    item.status = AssistanceStatus.completed
    item.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(item)

    return serialize_request(item, db)


@router.post("/requests/{request_id}/cancel")
def cancel_senior_sathi_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_user()),
):
    item = db.get(SeniorSathiRequest, request_id)

    if not item:
        raise HTTPException(status_code=404, detail="SeniorSathi request not found")

    item.status = AssistanceStatus.cancelled

    db.commit()
    db.refresh(item)

    return serialize_request(item, db)
