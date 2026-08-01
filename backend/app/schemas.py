from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models import (
    AlertSeverity,
    AlertStatus,
    AssistanceStatus,
    BookingSource,
    BookingStatus,
    UserRole,
    VisitPurpose,
)


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str
    phone: Optional[str] = None
    password: str = Field(min_length=6)
    role: UserRole = UserRole.pilgrim


class StaffCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str
    phone: Optional[str] = None
    password: str = Field(min_length=6)
    role: UserRole
    temple_id: Optional[int] = None
    department: Optional[str] = None
    gate_assigned: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    assigned_temples: list[int] = []

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
    state: str = "Gujarat"
    description: Optional[str] = None
    official_website: Optional[str] = None
    temple_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_capacity: int = 5000
    safe_capacity: int = 3500
    current_occupancy: int = 0
    entry_gates: int = 2
    exit_gates: int = 2
    emergency_contact: Optional[str] = None


class TempleOut(BaseModel):
    id: int
    name: str
    city: str
    state: Optional[str] = None
    description: Optional[str] = None
    official_website: Optional[str] = None
    temple_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_capacity: int
    safe_capacity: Optional[int] = None
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
    capacity: int = 300
    senior_reserved_capacity: int = 40


class TimeSlotOut(BaseModel):
    id: int
    temple_id: int
    temple_name: Optional[str] = None
    start_time: datetime
    end_time: datetime
    capacity: int
    booked_count: int
    senior_reserved_capacity: int
    senior_booked_count: int = 0
    is_active: bool
    available_count: int = 0
    available_capacity: int = 0

    model_config = {"from_attributes": True}


class BookingVisitorCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = None
    phone: Optional[str] = None
    is_senior: bool = False
    is_differently_abled: bool = False
    needs_wheelchair: bool = False
    id_type: Optional[str] = None
    id_last4: Optional[str] = None


class BookingCreate(BaseModel):
    temple_id: int
    slot_id: int

    visit_purpose: VisitPurpose = VisitPurpose.darshan

    primary_name: Optional[str] = None
    primary_age: Optional[int] = Field(default=None, ge=0, le=120)
    primary_gender: Optional[str] = None
    primary_phone: Optional[str] = None
    primary_email: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None

    visitor_count: int = Field(default=1, ge=1, le=50)
    senior_count: int = Field(default=0, ge=0, le=50)
    differently_abled_count: int = Field(default=0, ge=0, le=50)

    arrival_mode: Optional[str] = None
    expected_duration_minutes: int = Field(default=30, ge=5, le=300)
    preferred_language: str = "Hindi"

    needs_assistance: bool = False
    family_contact_name: Optional[str] = None
    family_contact_phone: Optional[str] = None

    is_vip: bool = False
    vip_reference: Optional[str] = None

    booking_notes: Optional[str] = None
    visitors: list[BookingVisitorCreate] = []


class KioskBookingCreate(BookingCreate):
    source: BookingSource = BookingSource.kiosk


class BookingVisitorOut(BaseModel):
    id: int
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    is_senior: bool
    is_differently_abled: bool
    needs_wheelchair: bool
    id_type: Optional[str] = None
    id_last4: Optional[str] = None

    model_config = {"from_attributes": True}


class BookingOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    temple_id: int
    slot_id: int
    ticket_code: str

    source: BookingSource = BookingSource.online
    visit_purpose: VisitPurpose = VisitPurpose.darshan

    primary_name: str
    primary_age: Optional[int] = None
    primary_gender: Optional[str] = None
    primary_phone: Optional[str] = None
    primary_email: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None

    visitor_count: int
    senior_count: int
    differently_abled_count: int

    arrival_mode: Optional[str] = None
    expected_duration_minutes: Optional[int] = None
    preferred_language: Optional[str] = None

    needs_assistance: bool = False
    family_contact_name: Optional[str] = None
    family_contact_phone: Optional[str] = None

    is_vip: bool = False
    vip_reference: Optional[str] = None

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
    visitors: list[BookingVisitorOut] = []

    model_config = {"from_attributes": True}


class CrowdReadingCreate(BaseModel):
    temple_id: int
    source: str = "manual"
    occupancy: int
    inflow_per_min: int = 0
    outflow_per_min: int = 0
    density_score: float = 0.0
    gate: Optional[str] = None
    zone: Optional[str] = None
    confidence: Optional[float] = None
    notes: Optional[str] = None


class CrowdReadingOut(BaseModel):
    id: int
    temple_id: int
    source: str
    occupancy: int
    inflow_per_min: int
    outflow_per_min: int
    density_score: float
    gate: Optional[str] = None
    zone: Optional[str] = None
    confidence: Optional[float] = None
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
    temple_name: Optional[str] = None
    title: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    location: Optional[str] = None
    instruction: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ParkingZoneCreate(BaseModel):
    temple_id: int
    name: str
    total_slots: int = 100
    available_slots: int = 100
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
    name: Optional[str] = None
    total_slots: Optional[int] = None
    available_slots: Optional[int] = None
    distance_label: Optional[str] = None
    route_hint: Optional[str] = None


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


class SeniorSathiRequestOut(BaseModel):
    id: int
    booking_id: int
    temple_id: int
    assistance_type: str
    status: AssistanceStatus
    assigned_volunteer_id: Optional[int] = None
    family_contact_name: Optional[str] = None
    family_contact_phone: Optional[str] = None
    priority_gate: str
    notes: Optional[str] = None
    created_at: datetime
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

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