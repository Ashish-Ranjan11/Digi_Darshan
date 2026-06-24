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
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, PyEnum):
    pilgrim = "pilgrim"
    admin = "admin"
    emergency_operator = "emergency_operator"
    scanner = "scanner"


class BookingStatus(str, PyEnum):
    booked = "booked"
    checked_in = "checked_in"
    completed = "completed"
    cancelled = "cancelled"


class AlertSeverity(str, PyEnum):
    info = "info"
    warning = "warning"
    critical = "critical"


class AlertStatus(str, PyEnum):
    active = "active"
    resolved = "resolved"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.pilgrim)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bookings = relationship("Booking", back_populates="user")


class Temple(Base):
    __tablename__ = "temples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    city = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    max_capacity = Column(Integer, default=5000)
    current_occupancy = Column(Integer, default=0)
    entry_gates = Column(Integer, default=2)
    exit_gates = Column(Integer, default=2)
    emergency_contact = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    slots = relationship("TimeSlot", back_populates="temple", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="temple")
    readings = relationship("CrowdReading", back_populates="temple", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="temple", cascade="all, delete-orphan")
    parking_zones = relationship("ParkingZone", back_populates="temple", cascade="all, delete-orphan")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    capacity = Column(Integer, nullable=False, default=200)
    booked_count = Column(Integer, nullable=False, default=0)
    senior_reserved_capacity = Column(Integer, nullable=False, default=20)
    is_active = Column(Boolean, default=True)

    temple = relationship("Temple", back_populates="slots")
    bookings = relationship("Booking", back_populates="slot")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)
    ticket_code = Column(String(80), unique=True, index=True, nullable=False)
    visitor_count = Column(Integer, nullable=False, default=1)
    senior_count = Column(Integer, nullable=False, default=0)
    differently_abled_count = Column(Integer, nullable=False, default=0)
    status = Column(Enum(BookingStatus), default=BookingStatus.booked, nullable=False)
    gate = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    checked_out_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="bookings")
    temple = relationship("Temple", back_populates="bookings")
    slot = relationship("TimeSlot", back_populates="bookings")


class CrowdReading(Base):
    __tablename__ = "crowd_readings"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)
    source = Column(String(60), default="manual")
    occupancy = Column(Integer, nullable=False)
    inflow_per_min = Column(Integer, default=0)
    outflow_per_min = Column(Integer, default=0)
    density_score = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    temple = relationship("Temple", back_populates="readings")


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


class ParkingZone(Base):
    __tablename__ = "parking_zones"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=False)
    name = Column(String(120), nullable=False)
    total_slots = Column(Integer, nullable=False, default=100)
    available_slots = Column(Integer, nullable=False, default=100)
    distance_label = Column(String(80), nullable=True)
    route_hint = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    temple_id = Column(Integer, ForeignKey("temples.id"), nullable=True)
    title = Column(String(160), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
