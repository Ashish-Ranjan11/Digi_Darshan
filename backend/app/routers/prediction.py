from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import CrowdReading, Temple, User, UserRole
from app.services.prediction_engine import build_prediction_payload

router = APIRouter(prefix="/prediction", tags=["prediction"])


@router.get("/{temple_id}")
def get_prediction(
    temple_id: int,
    festival_mode: bool = Query(default=False),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.emergency_operator)),
):
    temple = db.get(Temple, temple_id)

    if not temple:
        raise HTTPException(status_code=404, detail="Temple not found")

    readings = (
        db.query(CrowdReading)
        .filter(CrowdReading.temple_id == temple_id)
        .order_by(CrowdReading.created_at.desc())
        .limit(12)
        .all()
    )

    readings = list(reversed(readings))

    return build_prediction_payload(
        temple=temple,
        readings=readings,
        festival_mode=festival_mode,
    )
