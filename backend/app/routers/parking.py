from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import ParkingZone, Temple, TransportRoute, User, UserRole
from app.schemas import ParkingZoneCreate, ParkingZoneOut, ParkingZoneUpdate, TransportRouteOut
from app.websocket_manager import manager

router = APIRouter(prefix="/mobility", tags=["mobility"])


@router.get("/parking", response_model=list[ParkingZoneOut])
def list_parking(temple_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(ParkingZone).order_by(ParkingZone.name)
    if temple_id:
        query = query.filter(ParkingZone.temple_id == temple_id)
    return query.all()


@router.post("/parking", response_model=ParkingZoneOut, status_code=201)
def create_parking_zone(
    payload: ParkingZoneCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    temple = db.get(Temple, payload.temple_id)
    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")
    zone = ParkingZone(**payload.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.patch("/parking/{zone_id}", response_model=ParkingZoneOut)
async def update_parking_zone(
    zone_id: int,
    payload: ParkingZoneUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    zone = db.get(ParkingZone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Parking zone not found")
    zone.available_slots = min(payload.available_slots, zone.total_slots)
    db.commit()
    db.refresh(zone)
    await manager.broadcast(
        zone.temple_id,
        {
            "type": "parking_update",
            "temple_id": zone.temple_id,
            "zone": zone.name,
            "available_slots": zone.available_slots,
            "total_slots": zone.total_slots,
        },
    )
    return zone


@router.get("/routes", response_model=list[TransportRouteOut])
def list_transport_routes(temple_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(TransportRoute).order_by(TransportRoute.name)
    if temple_id:
        query = query.filter(TransportRoute.temple_id == temple_id)
    return query.all()
