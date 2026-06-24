from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import require_roles
from app.models import Alert, AlertStatus, Notification, Temple, User, UserRole
from app.schemas import AlertCreate, AlertOut
from app.websocket_manager import manager

router = APIRouter(prefix="/alerts", tags=["alerts"])


def serialize_alert(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "temple_id": alert.temple_id,
        "title": alert.title,
        "message": alert.message,
        "severity": alert.severity,
        "status": alert.status,
        "location": alert.location,
        "instruction": alert.instruction,
        "created_at": alert.created_at,
        "resolved_at": alert.resolved_at,
        "temple_name": alert.temple.name if alert.temple else None,
    }


@router.get("", response_model=list[AlertOut])
def list_alerts(active_only: bool = True, db: Session = Depends(get_db)):
    query = db.query(Alert).options(joinedload(Alert.temple)).order_by(Alert.created_at.desc())
    if active_only:
        query = query.filter(Alert.status == AlertStatus.active)
    return [serialize_alert(alert) for alert in query.limit(100).all()]


@router.post("", response_model=AlertOut, status_code=201)
async def create_alert(
    payload: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temple = db.get(Temple, payload.temple_id)
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")
    alert = Alert(**payload.model_dump(), created_by_id=current_user.id)
    db.add(alert)
    db.add(
        Notification(
            temple_id=temple.id,
            title=f"{payload.severity.value.upper()}: {payload.title}",
            message=payload.instruction or payload.message,
        )
    )
    db.commit()
    db.refresh(alert)
    alert = db.query(Alert).options(joinedload(Alert.temple)).filter(Alert.id == alert.id).first()
    data = serialize_alert(alert)
    await manager.broadcast(temple.id, {"type": "alert", **data})
    return data


@router.patch("/{alert_id}/resolve", response_model=AlertOut)
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    alert = db.query(Alert).options(joinedload(Alert.temple)).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus.resolved
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    data = serialize_alert(alert)
    await manager.broadcast(alert.temple_id, {"type": "alert_resolved", **data})
    return data
