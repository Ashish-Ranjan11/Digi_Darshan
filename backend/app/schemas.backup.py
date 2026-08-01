
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models import AlertSeverity, AlertStatus, BookingStatus, UserRole


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str
    phone: Optional[str] = None
    password: str = Field(min_length=6)
    role: UserRole = UserRole.pilgrim


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TempleCreate(BaseModel):
    name: str
    city: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_capacity: int = 5000
    current_occupancy: int = 0
    entry_gates: int = 2
    exit_gates: int = 2
    emergency_contact: Optional[str] = None


class TempleOut(BaseModel):
    id: int
    name: str
    city: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_capacity: int
    current_occupancy: int
    entry_gates: int
    exit_gates: int
    emergency_contact: Optional[str] = None
    is_active: bool
    occupancy_percent: float = 0
    crowd_level: str = "low"

    model_config = {"from_attributes": True}


class TimeSlotCreate(BaseModel):
    temple_id: int
    start_time: datetime
    end_time: datetime
    capacity: int = 200
    senior_reserved_capacity: int = 20


class TimeSlotOut(BaseModel):
    id: int
    temple_id: int
    start_time: datetime
    end_time: datetime
    capacity: int
    booked_count: int
    senior_reserved_capacity: int
    is_active: bool
    available_count: int

    model_config = {"from_attributes": True}


class BookingCreate(BaseModel):
    temple_id: int
    slot_id: int
    visitor_count: int = Field(default=1, ge=1, le=10)
    senior_count: int = Field(default=0, ge=0, le=10)
    differently_abled_count: int = Field(default=0, ge=0, le=10)


class BookingOut(BaseModel):
    id: int
    user_id: int
    temple_id: int
    slot_id: int
    ticket_code: str
    visitor_count: int
    senior_count: int
    differently_abled_count: int
    status: BookingStatus
    gate: Optional[str] = None
    created_at: datetime
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    temple_name: Optional[str] = None
    temple_city: Optional[str] = None
    slot_start: Optional[datetime] = None
    slot_end: Optional[datetime] = None
    qr_svg: Optional[str] = None

    model_config = {"from_attributes": True}


class CrowdReadingCreate(BaseModel):
    temple_id: int
    source: str = "manual"
    occupancy: int = Field(ge=0)
    inflow_per_min: int = 0
    outflow_per_min: int = 0
    density_score: float = 0.0
    notes: Optional[str] = None


class CrowdReadingOut(BaseModel):
    id: int
    temple_id: int
    source: str
    occupancy: int
    inflow_per_min: int
    outflow_per_min: int
    density_score: float
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertCreate(BaseModel):
    temple_id: int
    title: str
    message: str
    severity: AlertSeverity = AlertSeverity.info
    location: Optional[str] = None
    instruction: Optional[str] = None


class AlertOut(BaseModel):
    id: int
    temple_id: int
    title: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    location: Optional[str] = None
    instruction: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    temple_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ParkingZoneCreate(BaseModel):
    temple_id: int
    name: str
    total_slots: int
    available_slots: int
    distance_label: Optional[str] = None
    route_hint: Optional[str] = None


class ParkingZoneOut(BaseModel):
    id: int
    temple_id: int
    name: str
    total_slots: int
    available_slots: int
    distance_label: Optional[str] = None
    route_hint: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParkingZoneUpdate(BaseModel):
    available_slots: int = Field(ge=0)


class TransportRouteOut(BaseModel):
    id: int
    temple_id: int
    name: str
    mode: str
    start_point: str
    end_point: str
    frequency_minutes: int
    status: str
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class ScannerRequest(BaseModel):
    ticket_code: str
    gate: str = "Gate A"


class DashboardOverview(BaseModel):
    temples: int
    active_alerts: int
    bookings_today: int
    visitors_expected_today: int
    total_current_occupancy: int
    average_occupancy_percent: float
    latest_readings: list[CrowdReadingOut]
    active_alert_list: list[AlertOut]


class NotificationOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    temple_id: Optional[int] = None
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
class ControlActionCreate(BaseModel):
    temple_id: int
    action_type: str
    title: Optional[str] = None
    instruction: Optional[str] = None
    severity: str = "warning"
    location: Optional[str] = None


class ControlActionOut(BaseModel):
    id: int
    temple_id: int
    action_type: str
    title: str
    instruction: str
    severity: str
    location: Optional[str] = None
    status: str
    created_by_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    temple_name: Optional[str] = None
    created_by_name: Optional[str] = None

    model_config = {"from_attributes": True}
