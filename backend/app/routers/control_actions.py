from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import require_roles
from app.models import (
    Alert,
    AlertSeverity,
    ControlAction,
    Notification,
    Temple,
    User,
    UserRole,
)
from app.schemas import ControlActionCreate, ControlActionOut
from app.websocket_manager import manager

router = APIRouter(prefix="/control-actions", tags=["control-actions"])


ACTION_TEMPLATES = {
    "pause_entry": {
        "label": "Pause Entry",
        "title": "Entry Temporarily Paused",
        "instruction": "New entry has been paused temporarily. Pilgrims are requested to stay calm and follow queue volunteers.",
        "severity": "critical",
        "location": "Main Entry Gate",
    },
    "open_gate_b": {
        "label": "Open Gate B",
        "title": "Gate B Opened for Diversion",
        "instruction": "Pilgrims near Gate A should move towards Gate B as guided by volunteers.",
        "severity": "warning",
        "location": "Gate B",
    },
    "activate_emergency_exit": {
        "label": "Activate Emergency Exit",
        "title": "Emergency Exit Route Activated",
        "instruction": "Use the marked emergency exit corridor. Avoid crowding near the main queue and follow security instructions.",
        "severity": "critical",
        "location": "Emergency Exit Corridor",
    },
    "divert_to_gate_c": {
        "label": "Divert to Gate C",
        "title": "Crowd Diverted to Gate C",
        "instruction": "Pilgrims are being diverted to Gate C to reduce pressure near the main queue corridor.",
        "severity": "warning",
        "location": "Gate C",
    },
    "redirect_parking": {
        "label": "Redirect Parking",
        "title": "Parking Diversion Activated",
        "instruction": "Primary parking is filling quickly. Vehicles should move towards the secondary parking zone and use shuttle support.",
        "severity": "warning",
        "location": "Parking Zone",
    },
    "increase_shuttle": {
        "label": "Increase Shuttle Frequency",
        "title": "Additional Shuttle Movement Started",
        "instruction": "Additional shuttle frequency has been activated for smoother pilgrim arrival and departure.",
        "severity": "info",
        "location": "Shuttle Route",
    },
    "senior_priority_route": {
        "label": "Activate SeniorSathi Route",
        "title": "Senior Citizen Priority Route Activated",
        "instruction": "Senior citizens and differently-abled pilgrims may use the priority assistance route with family support.",
        "severity": "info",
        "location": "SeniorSathi Assistance Route",
    },
    "resume_normal_flow": {
        "label": "Resume Normal Flow",
        "title": "Normal Crowd Flow Resumed",
        "instruction": "Crowd movement has returned to normal. Standard queue and entry operations may continue.",
        "severity": "info",
        "location": "Temple Premises",
    },
}


def serialize_action(action: ControlAction, temple_name: str | None = None, created_by_name: str | None = None):
    return {
        "id": action.id,
        "temple_id": action.temple_id,
        "action_type": action.action_type,
        "title": action.title,
        "instruction": action.instruction,
        "severity": action.severity,
        "location": action.location,
        "status": action.status,
        "created_by_id": action.created_by_id,
        "created_at": action.created_at,
        "resolved_at": action.resolved_at,
        "temple_name": temple_name,
        "created_by_name": created_by_name,
    }


@router.get("/templates")
def get_action_templates():
    return [
        {
            "action_type": key,
            **value,
        }
        for key, value in ACTION_TEMPLATES.items()
    ]


@router.get("/{temple_id}", response_model=list[ControlActionOut])
def list_control_actions(
    temple_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temple = db.get(Temple, temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    actions = (
        db.query(ControlAction)
        .filter(ControlAction.temple_id == temple_id)
        .order_by(ControlAction.created_at.desc())
        .limit(50)
        .all()
    )

    user_ids = [action.created_by_id for action in actions if action.created_by_id]
    users = {}

    if user_ids:
        users = {
            user.id: user.name
            for user in db.query(User).filter(User.id.in_(user_ids)).all()
        }

    return [
        serialize_action(
            action,
            temple_name=temple.name,
            created_by_name=users.get(action.created_by_id),
        )
        for action in actions
    ]


@router.post("", response_model=ControlActionOut, status_code=201)
async def create_control_action(
    payload: ControlActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temple = db.get(Temple, payload.temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    template = ACTION_TEMPLATES.get(payload.action_type)

    if not template and not payload.title:
        raise HTTPException(
            status_code=400,
            detail="Invalid action_type. Use /api/control-actions/templates to see supported actions.",
        )

    title = payload.title or template["title"]
    instruction = payload.instruction or template["instruction"]
    severity = payload.severity or template.get("severity", "warning")
    location = payload.location or template.get("location")

    action = ControlAction(
        temple_id=temple.id,
        action_type=payload.action_type,
        title=title,
        instruction=instruction,
        severity=severity,
        location=location,
        status="active",
        created_by_id=current_user.id,
    )

    db.add(action)

    alert_severity = AlertSeverity.info

    if severity == "warning":
        alert_severity = AlertSeverity.warning
    elif severity == "critical":
        alert_severity = AlertSeverity.critical

    alert = Alert(
        temple_id=temple.id,
        title=title,
        message=instruction,
        severity=alert_severity,
        location=location,
        instruction=instruction,
        created_by_id=current_user.id,
    )

    db.add(alert)

    db.add(
        Notification(
            temple_id=temple.id,
            title=f"CONTROL ACTION: {title}",
            message=instruction,
        )
    )

    db.commit()
    db.refresh(action)

    data = serialize_action(
        action,
        temple_name=temple.name,
        created_by_name=current_user.name,
    )

    await manager.broadcast(
        temple.id,
        {
            "type": "control_action",
            **data,
        },
    )

    return data


@router.patch("/{action_id}/resolve", response_model=ControlActionOut)
async def resolve_control_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    action = db.get(ControlAction, action_id)

    if not action:
        raise HTTPException(status_code=404, detail="Control action not found")

    temple = db.get(Temple, action.temple_id)

    action.status = "resolved"
    action.resolved_at = datetime.now(timezone.utc)

    db.add(
        Notification(
            temple_id=action.temple_id,
            title=f"RESOLVED: {action.title}",
            message=f"The control-room action has been resolved by {current_user.name}.",
        )
    )

    db.commit()
    db.refresh(action)

    data = serialize_action(
        action,
        temple_name=temple.name if temple else None,
        created_by_name=current_user.name,
    )

    await manager.broadcast(
        action.temple_id,
        {
            "type": "control_action_resolved",
            **data,
        },
    )

    return data
