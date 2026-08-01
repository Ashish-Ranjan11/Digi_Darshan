from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, PyEnum):
    pilgrim = "pilgrim"
    admin = "admin"
    super_admin = "super_admin"
    temple_admin = "temple_admin"
    emergency_operator = "emergency_operator"
    scanner = "scanner"
    kiosk_operator = "kiosk_operator"
    senior_sathi_volunteer = "senior_sathi_volunteer"
    security_officer = "security_officer"
    vip_coordinator = "vip_coordinator"


class BookingStatus(str, PyEnum):
    booked = "booked"
    checked_in = "checked_in"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class VisitPurpose(str, PyEnum):
    darshan = "darshan"
    aarti = "aarti"
    special_puja = "special_puja"
    festival_mela = "festival_mela"
    senior_sathi = "senior_sathi"
    vip_visit = "vip_visit"
    group_visit = "group_visit"
    walk_in = "walk_in"


class BookingSource(str, PyEnum):
    online = "online"
    kiosk = "kiosk"
    helpdesk = "helpdesk"
    walk_in = "walk_in"
    admin = "admin"


class AssistanceStatus(str, PyEnum):
    not_required = "not_required"
    pending = "pending"
    assigned = "assigned"
    completed = "completed"
    cancelled = "cancelled"


class AlertSeverity(str, PyEnum):
    info = "info"
    warning = "warning"
    critical = "critical"


class AlertStatus(str, PyEnum):
    active = "active"
    resolved = "resolved"


class FestivalModeStatus(str, PyEnum):
    planned = "planned"
    active = "active"
    completed = "completed"


class VIPMovementStatus(str, PyEnum):
    scheduled = "scheduled"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)

    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.pilgrim)

    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bookings = relationship(
        "Booking",
        back_populates="user",
        foreign_keys="Booking.user_id",
    )

    staff_assignments = relationship(
        "TempleStaff",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Temple(Base):
    __tablename__ = "temples"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(160), nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(120), default="Gujarat")
    description = Column(Text, nullable=True)

    official_website = Column(String(255), nullable=True)
    temple_code = Column(String(20), unique=True, nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    max_capacity = Column(Integer, default=5000)
    safe_capacity = Column(Integer, default=3500)
    current_occupancy = Column(Integer, default=0)

    entry_gates = Column(Integer, default=2)
    exit_gates = Column(Integer, default=2)

    emergency_contact = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    slots = relationship(
        "TimeSlot",
        back_populates="temple",
        cascade="all, delete-orphan",
    )

    bookings = relationship(
        "Booking",
        back_populates="temple",
        cascade="all, delete-orphan",
    )

    readings = relationship(
        "CrowdReading",
        back_populates="temple",
        cascade="all, delete-orphan",
    )

    alerts = relationship(
        "Alert",
        back_populates="temple",
        cascade="all, delete-orphan",
    )

    parking_zones = relationship(
        "ParkingZone",
        back_populates="temple",
        cascade="all, delete-orphan",
    )

    staff = relationship(
        "TempleStaff",
        back_populates="temple",
        cascade="all, delete-orphan",
    )


class TempleStaff(Base):
    __tablename__ = "temple_staff"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    role = Column(Enum(UserRole), nullable=False)
    department = Column(String(120), nullable=True)
    gate_assigned = Column(String(80), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    temple = relationship("Temple", back_populates="staff")
    user = relationship("User", back_populates="staff_assignments")

    __table_args__ = (
        UniqueConstraint("temple_id", "user_id", name="uq_temple_staff_user"),
    )


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    capacity = Column(Integer, nullable=False, default=300)
    booked_count = Column(Integer, nullable=False, default=0)

    senior_reserved_capacity = Column(Integer, nullable=False, default=40)
    senior_booked_count = Column(Integer, nullable=False, default=0)

    slot_type = Column(String(80), default="normal")
    is_festival_slot = Column(Boolean, default=False)
    is_vip_blocked = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    temple = relationship("Temple", back_populates="slots")
    bookings = relationship("Booking", back_populates="slot")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)

    ticket_code = Column(String(80), unique=True, index=True, nullable=False)

    source = Column(Enum(BookingSource), nullable=False, default=BookingSource.online)
    visit_purpose = Column(Enum(VisitPurpose), nullable=False, default=VisitPurpose.darshan)

    primary_name = Column(String(120), nullable=False)
    primary_age = Column(Integer, nullable=True)
    primary_gender = Column(String(30), nullable=True)
    primary_phone = Column(String(20), nullable=True)
    primary_email = Column(String(150), nullable=True)

    city = Column(String(120), nullable=True)
    state = Column(String(120), nullable=True)

    visitor_count = Column(Integer, nullable=False, default=1)
    senior_count = Column(Integer, nullable=False, default=0)
    differently_abled_count = Column(Integer, nullable=False, default=0)

    arrival_mode = Column(String(80), nullable=True)
    expected_duration_minutes = Column(Integer, default=30)
    preferred_language = Column(String(50), default="Hindi")

    needs_assistance = Column(Boolean, default=False)
    family_contact_name = Column(String(120), nullable=True)
    family_contact_phone = Column(String(20), nullable=True)

    is_vip = Column(Boolean, default=False)
    vip_reference = Column(String(180), nullable=True)

    status = Column(Enum(BookingStatus), default=BookingStatus.booked, nullable=False)
    gate = Column(String(80), nullable=True)

    ticket_sent_to = Column(String(150), nullable=True)
    booking_notes = Column(Text, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    checked_out_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship(
        "User",
        back_populates="bookings",
        foreign_keys=[user_id],
    )

    temple = relationship("Temple", back_populates="bookings")
    slot = relationship("TimeSlot", back_populates="bookings")

    visitors = relationship(
        "BookingVisitor",
        back_populates="booking",
        cascade="all, delete-orphan",
    )

    senior_sathi_request = relationship(
        "SeniorSathiRequest",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan",
    )


class BookingVisitor(Base):
    __tablename__ = "booking_visitors"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)

    full_name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(30), nullable=True)
    phone = Column(String(20), nullable=True)

    is_senior = Column(Boolean, default=False)
    is_differently_abled = Column(Boolean, default=False)
    needs_wheelchair = Column(Boolean, default=False)

    id_type = Column(String(80), nullable=True)
    id_last4 = Column(String(10), nullable=True)

    booking = relationship("Booking", back_populates="visitors")


class SeniorSathiRequest(Base):
    __tablename__ = "senior_sathi_requests"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    assistance_type = Column(String(120), default="general_assistance")
    status = Column(Enum(AssistanceStatus), default=AssistanceStatus.pending)

    assigned_volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    family_contact_name = Column(String(120), nullable=True)
    family_contact_phone = Column(String(20), nullable=True)

    priority_gate = Column(String(80), default="SeniorSathi Gate")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    booking = relationship("Booking", back_populates="senior_sathi_request")


class FestivalMode(Base):
    __tablename__ = "festival_modes"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    name = Column(String(160), nullable=False)
    status = Column(Enum(FestivalModeStatus), default=FestivalModeStatus.planned)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    expected_footfall = Column(Integer, default=0)
    surge_multiplier = Column(Float, default=1.5)

    rules = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VIPMovement(Base):
    __tablename__ = "vip_movements"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    title = Column(String(180), nullable=False)
    vip_category = Column(String(120), nullable=True)

    arrival_time = Column(DateTime(timezone=True), nullable=False)
    departure_time = Column(DateTime(timezone=True), nullable=True)

    route_lockdown_required = Column(Boolean, default=True)
    public_booking_pause_required = Column(Boolean, default=False)

    affected_gates = Column(String(255), nullable=True)
    instructions = Column(Text, nullable=True)

    status = Column(Enum(VIPMovementStatus), default=VIPMovementStatus.scheduled)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CrowdReading(Base):
    __tablename__ = "crowd_readings"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    source = Column(String(60), default="manual")
    occupancy = Column(Integer, nullable=False)
    inflow_per_min = Column(Integer, default=0)
    outflow_per_min = Column(Integer, default=0)
    density_score = Column(Float, default=0.0)

    gate = Column(String(80), nullable=True)
    zone = Column(String(120), nullable=True)
    confidence = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    temple = relationship("Temple", back_populates="readings")


class HeatmapZone(Base):
    __tablename__ = "heatmap_zones"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    zone_name = Column(String(120), nullable=False)
    zone_type = Column(String(80), default="queue")
    crowd_level = Column(String(40), default="low")

    density_score = Column(Float, default=0.0)
    occupancy = Column(Integer, default=0)
    max_capacity = Column(Integer, default=500)

    recommended_action = Column(Text, nullable=True)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class SensorEvent(Base):
    __tablename__ = "sensor_events"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    source = Column(String(120), nullable=False)
    sensor_type = Column(String(80), default="crowd_counter")

    gate = Column(String(80), nullable=True)
    zone = Column(String(120), nullable=True)

    occupancy = Column(Integer, nullable=True)
    inflow_per_min = Column(Integer, default=0)
    outflow_per_min = Column(Integer, default=0)
    density_score = Column(Float, default=0.0)
    confidence = Column(Float, nullable=True)

    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScannerLog(Base):
    __tablename__ = "scanner_logs"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True)

    ticket_code = Column(String(80), nullable=False)
    action = Column(String(40), nullable=False)
    gate = Column(String(80), nullable=False)

    status = Column(String(40), nullable=False)
    message = Column(Text, nullable=True)

    scanned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GateEvent(Base):
    __tablename__ = "gate_events"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)

    gate = Column(String(80), nullable=False)
    event_type = Column(String(40), nullable=False)
    visitor_count = Column(Integer, default=0)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    title = Column(String(160), nullable=False)
    message = Column(Text, nullable=False)

    severity = Column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.info)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.active)

    location = Column(String(180), nullable=True)
    instruction = Column(Text, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    temple = relationship("Temple", back_populates="alerts")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True)

    title = Column(String(160), nullable=False)
    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ParkingZone(Base):
    __tablename__ = "parking_zones"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    name = Column(String(120), nullable=False)
    total_slots = Column(Integer, nullable=False, default=100)
    available_slots = Column(Integer, nullable=False, default=100)

    distance_label = Column(String(80), nullable=True)
    route_hint = Column(Text, nullable=True)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    temple = relationship("Temple", back_populates="parking_zones")


class TransportRoute(Base):
    __tablename__ = "transport_routes"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    name = Column(String(120), nullable=False)
    mode = Column(String(40), nullable=False, default="shuttle")

    start_point = Column(String(160), nullable=False)
    end_point = Column(String(160), nullable=False)

    frequency_minutes = Column(Integer, default=15)
    status = Column(String(80), default="On time")
    notes = Column(Text, nullable=True)


class ControlAction(Base):
    __tablename__ = "control_actions"

    id = Column(Integer, primary_key=True, index=True)

    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)

    action_type = Column(String(80), nullable=False)
    title = Column(String(180), nullable=False)
    instruction = Column(Text, nullable=False)

    severity = Column(String(30), default="warning")
    location = Column(String(180), nullable=True)

    status = Column(String(30), default="active")

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True)

    action = Column(String(120), nullable=False)
    entity_type = Column(String(120), nullable=True)
    entity_id = Column(Integer, nullable=True)

    details = Column(Text, nullable=True)
    ip_address = Column(String(80), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())