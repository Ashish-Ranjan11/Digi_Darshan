from datetime import datetime, time, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import require_roles
from app.models import Alert, AlertStatus, Booking, CrowdReading, Temple, User, UserRole
from app.routers.alerts import serialize_alert
from app.schemas import DashboardOverview

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temples = db.query(Temple).filter(Temple.is_active.is_(True)).all()
    temple_count = len(temples)
    active_alerts = db.query(Alert).filter(Alert.status == AlertStatus.active).count()

    today_start = datetime.combine(datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc)
    bookings_today_q = db.query(Booking).filter(Booking.created_at >= today_start)
    bookings_today = bookings_today_q.count()
    visitors_expected_today = bookings_today_q.with_entities(func.coalesce(func.sum(Booking.visitor_count), 0)).scalar() or 0

    total_current_occupancy = sum(t.current_occupancy for t in temples)
    avg_percent = 0.0
    if temples:
        avg_percent = round(
            sum((t.current_occupancy / t.max_capacity) * 100 if t.max_capacity else 0 for t in temples) / len(temples), 2
        )

    latest_readings = db.query(CrowdReading).order_by(CrowdReading.created_at.desc()).limit(8).all()
    active_alert_list = (
        db.query(Alert)
        .options(joinedload(Alert.temple))
        .filter(Alert.status == AlertStatus.active)
        .order_by(Alert.created_at.desc())
        .limit(8)
        .all()
    )

    return {
        "temples": temple_count,
        "active_alerts": active_alerts,
        "bookings_today": bookings_today,
        "visitors_expected_today": visitors_expected_today,
        "total_current_occupancy": total_current_occupancy,
        "average_occupancy_percent": avg_percent,
        "latest_readings": latest_readings,
        "active_alert_list": [serialize_alert(alert) for alert in active_alert_list],
    }
