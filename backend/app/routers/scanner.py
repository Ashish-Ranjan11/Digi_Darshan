from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import GateEvent, ScannerLog, Temple, User, UserRole
from app.schemas import ScannerRequest
from app.services.gate_flow_engine import process_gate_scan, verify_ticket_only
from app.websocket_manager import manager

router = APIRouter(prefix="/scanner", tags=["scanner"])


def serialize_log(log: ScannerLog) -> dict:
    return {
        "id": log.id,
        "booking_id": log.booking_id,
        "temple_id": log.temple_id,
        "ticket_code": log.ticket_code,
        "action": log.action,
        "gate": log.gate,
        "status": log.status,
        "message": log.message,
        "scanned_by_id": log.scanned_by_id,
        "created_at": log.created_at,
    }


@router.post("/verify")
def verify_ticket(
    payload: ScannerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.scanner)),
):
    return verify_ticket_only(
        db,
        ticket_code=payload.ticket_code,
        gate=payload.gate,
        current_user=current_user,
    )


@router.post("/check-in")
async def check_in(
    payload: ScannerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.scanner)),
):
    result, websocket_payload = process_gate_scan(
        db,
        ticket_code=payload.ticket_code,
        gate=payload.gate,
        action="check-in",
        current_user=current_user,
    )

    await manager.broadcast(result["temple_id"], websocket_payload)

    return result


@router.post("/check-out")
async def check_out(
    payload: ScannerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.scanner)),
):
    result, websocket_payload = process_gate_scan(
        db,
        ticket_code=payload.ticket_code,
        gate=payload.gate,
        action="check-out",
        current_user=current_user,
    )

    await manager.broadcast(result["temple_id"], websocket_payload)

    return result


@router.get("/logs/{temple_id}")
def scanner_logs(
    temple_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.scanner, UserRole.emergency_operator)),
):
    temple = db.get(Temple, temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    logs = (
        db.query(ScannerLog)
        .filter(ScannerLog.temple_id == temple_id)
        .order_by(ScannerLog.created_at.desc())
        .limit(50)
        .all()
    )

    return [serialize_log(log) for log in logs]


@router.get("/gate-flow/{temple_id}")
def gate_flow_stats(
    temple_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.scanner, UserRole.emergency_operator)),
):
    temple = db.get(Temple, temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    today_start = datetime.now(timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    events = (
        db.query(GateEvent)
        .filter(GateEvent.temple_id == temple_id)
        .filter(GateEvent.created_at >= today_start)
        .order_by(GateEvent.created_at.desc())
        .all()
    )

    logs = (
        db.query(ScannerLog)
        .filter(ScannerLog.temple_id == temple_id)
        .order_by(ScannerLog.created_at.desc())
        .limit(10)
        .all()
    )

    gate_map: dict[str, dict] = {}

    for event in events:
        if event.gate not in gate_map:
            gate_map[event.gate] = {
                "gate": event.gate,
                "check_ins": 0,
                "check_outs": 0,
                "net_flow": 0,
            }

        if event.event_type == "check_in":
            gate_map[event.gate]["check_ins"] += event.visitor_count
            gate_map[event.gate]["net_flow"] += event.visitor_count

        if event.event_type == "check_out":
            gate_map[event.gate]["check_outs"] += event.visitor_count
            gate_map[event.gate]["net_flow"] -= event.visitor_count

    total_checkins = sum(item["check_ins"] for item in gate_map.values())
    total_checkouts = sum(item["check_outs"] for item in gate_map.values())

    occupancy_percent = (
        round((temple.current_occupancy / temple.max_capacity) * 100, 2)
        if temple.max_capacity
        else 0
    )

    if occupancy_percent >= 90:
        level = "critical"
    elif occupancy_percent >= 70:
        level = "high"
    elif occupancy_percent >= 45:
        level = "medium"
    else:
        level = "low"

    return {
        "temple_id": temple.id,
        "temple_name": temple.name,
        "city": temple.city,
        "current_occupancy": temple.current_occupancy,
        "max_capacity": temple.max_capacity,
        "occupancy_percent": occupancy_percent,
        "crowd_level": level,
        "total_checkins_today": total_checkins,
        "total_checkouts_today": total_checkouts,
        "net_flow_today": total_checkins - total_checkouts,
        "gate_counts": list(gate_map.values()),
        "recent_logs": [serialize_log(log) for log in logs],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }