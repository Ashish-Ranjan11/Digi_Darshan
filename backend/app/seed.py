from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import (
    Alert,
    AlertSeverity,
    Booking,
    BookingSource,
    BookingStatus,
    BookingVisitor,
    CrowdReading,
    Notification,
    ParkingZone,
    Temple,
    TempleStaff,
    TimeSlot,
    TransportRoute,
    User,
    UserRole,
    VisitPurpose,
)
from app.security import get_password_hash


def create_user(db, name, email, role, password, phone=None):
    existing = db.query(User).filter(User.email == email.lower()).first()

    if existing:
        return existing

    user = User(
        name=name,
        email=email.lower(),
        phone=phone,
        role=role,
        password_hash=get_password_hash(password),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_temple(
    db,
    name,
    city,
    code,
    max_capacity,
    safe_capacity,
    current_occupancy,
    entry_gates,
    exit_gates,
):
    existing = db.query(Temple).filter(Temple.temple_code == code).first()

    if existing:
        return existing

    temple = Temple(
        name=name,
        city=city,
        state="Gujarat",
        temple_code=code,
        description=f"{name} smart pilgrimage management zone.",
        official_website=None,
        max_capacity=max_capacity,
        safe_capacity=safe_capacity,
        current_occupancy=current_occupancy,
        entry_gates=entry_gates,
        exit_gates=exit_gates,
        emergency_contact="108",
        is_active=True,
    )

    db.add(temple)
    db.commit()
    db.refresh(temple)

    return temple


def assign_staff(db, user, temple, role, department=None, gate=None):
    existing = (
        db.query(TempleStaff)
        .filter(TempleStaff.user_id == user.id)
        .filter(TempleStaff.temple_id == temple.id)
        .first()
    )

    if existing:
        return existing

    assignment = TempleStaff(
        temple_id=temple.id,
        user_id=user.id,
        role=role,
        department=department,
        gate_assigned=gate,
        is_active=True,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment


def create_slots(db, temple):
    now = datetime.now()
    today = now.date()

    for day_offset in range(7):
        target_date = today + timedelta(days=day_offset)

        for hour in range(6, 18):
            start_time = datetime.combine(target_date, datetime.min.time()).replace(
                hour=hour
            )
            end_time = start_time + timedelta(hours=1)

            existing = (
                db.query(TimeSlot)
                .filter(TimeSlot.temple_id == temple.id)
                .filter(TimeSlot.start_time == start_time)
                .first()
            )

            if existing:
                continue

            slot = TimeSlot(
                temple_id=temple.id,
                start_time=start_time,
                end_time=end_time,
                capacity=300,
                booked_count=0,
                senior_reserved_capacity=40,
                senior_booked_count=0,
                slot_type="normal",
                is_festival_slot=False,
                is_vip_blocked=False,
                is_active=True,
            )

            db.add(slot)

    db.commit()


def create_parking(db, temple):
    zones = [
        ("Main Parking", 500, 420, "300m from temple"),
        ("Bus Parking", 300, 260, "700m from temple"),
        ("SeniorSathi Parking", 80, 70, "Near priority entry"),
    ]

    for name, total, available, distance in zones:
        existing = (
            db.query(ParkingZone)
            .filter(ParkingZone.temple_id == temple.id)
            .filter(ParkingZone.name == name)
            .first()
        )

        if existing:
            continue

        zone = ParkingZone(
            temple_id=temple.id,
            name=name,
            total_slots=total,
            available_slots=available,
            distance_label=distance,
            route_hint="Follow Digii-Flowmaster parking guidance.",
        )

        db.add(zone)

    db.commit()


def create_transport(db, temple):
    existing = db.query(TransportRoute).filter(
        TransportRoute.temple_id == temple.id
    ).first()

    if existing:
        return

    routes = [
        ("Temple Shuttle A", "shuttle", "Main Parking", "Temple Gate A", 10),
        ("SeniorSathi Shuttle", "shuttle", "SeniorSathi Parking", "Priority Gate", 8),
    ]

    for name, mode, start, end, frequency in routes:
        route = TransportRoute(
            temple_id=temple.id,
            name=name,
            mode=mode,
            start_point=start,
            end_point=end,
            frequency_minutes=frequency,
            status="On time",
            notes="Demo transport route.",
        )

        db.add(route)

    db.commit()


def create_initial_crowd(db, temple):
    existing = db.query(CrowdReading).filter(
        CrowdReading.temple_id == temple.id
    ).first()

    if existing:
        return

    reading = CrowdReading(
        temple_id=temple.id,
        source="seed_demo",
        occupancy=temple.current_occupancy,
        inflow_per_min=25,
        outflow_per_min=18,
        density_score=0.35,
        gate="Gate A",
        zone="Main Queue",
        confidence=0.9,
        notes="Initial demo crowd reading.",
    )

    db.add(reading)
    db.commit()


def create_demo_booking(db, pilgrim, temple):
    existing = db.query(Booking).filter(Booking.user_id == pilgrim.id).first()

    if existing:
        return existing

    slot = (
        db.query(TimeSlot)
        .filter(TimeSlot.temple_id == temple.id)
        .filter(TimeSlot.end_time >= datetime.now())
        .order_by(TimeSlot.start_time.asc())
        .first()
    )

    if not slot:
        return None

    booking = Booking(
        user_id=pilgrim.id,
        temple_id=temple.id,
        slot_id=slot.id,
        ticket_code=f"{temple.temple_code}-DEMO12345",
        source=BookingSource.online,
        visit_purpose=VisitPurpose.darshan,
        primary_name=pilgrim.name,
        primary_age=22,
        primary_gender="Male",
        primary_phone=pilgrim.phone,
        primary_email=pilgrim.email,
        city="Ahmedabad",
        state="Gujarat",
        visitor_count=2,
        senior_count=0,
        differently_abled_count=0,
        arrival_mode="Bus",
        expected_duration_minutes=30,
        preferred_language="Hindi",
        needs_assistance=False,
        status=BookingStatus.booked,
        gate="Gate A",
        ticket_sent_to=pilgrim.email,
        booking_notes="Demo booking.",
        created_by_id=pilgrim.id,
    )

    slot.booked_count += 2

    db.add(booking)
    db.flush()

    visitor = BookingVisitor(
        booking_id=booking.id,
        full_name=pilgrim.name,
        age=22,
        gender="Male",
        phone=pilgrim.phone,
        is_senior=False,
        is_differently_abled=False,
        needs_wheelchair=False,
    )

    db.add(visitor)

    notification = Notification(
        user_id=pilgrim.id,
        temple_id=temple.id,
        title="Demo ticket confirmed",
        message=f"Your demo ticket {booking.ticket_code} is confirmed.",
    )

    db.add(notification)
    db.commit()
    db.refresh(booking)

    return booking


def create_alert(db, temple, admin):
    existing = db.query(Alert).filter(Alert.temple_id == temple.id).first()

    if existing:
        return

    alert = Alert(
        temple_id=temple.id,
        title="Demo crowd advisory",
        message="Moderate crowd near main queue zone.",
        severity=AlertSeverity.info,
        location="Main Queue",
        instruction="Please follow queue marshal instructions.",
        created_by_id=admin.id,
    )

    db.add(alert)
    db.commit()


def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        admin = create_user(
            db,
            "System Admin",
            "admin@digidarshan.in",
            UserRole.admin,
            "Admin@123",
            "9000000001",
        )

        super_admin = create_user(
            db,
            "State Super Admin",
            "superadmin@digidarshan.in",
            UserRole.super_admin,
            "Super@123",
            "9000000002",
        )

        pilgrim = create_user(
            db,
            "Demo Pilgrim",
            "pilgrim@digidarshan.in",
            UserRole.pilgrim,
            "Pilgrim@123",
            "9000000003",
        )

        scanner = create_user(
            db,
            "Scanner Staff",
            "scanner@digidarshan.in",
            UserRole.scanner,
            "Scanner@123",
            "9000000004",
        )

        operator = create_user(
            db,
            "Crowd Operator",
            "operator@digidarshan.in",
            UserRole.emergency_operator,
            "Operator@123",
            "9000000005",
        )

        kiosk = create_user(
            db,
            "Kiosk Operator",
            "kiosk@digidarshan.in",
            UserRole.kiosk_operator,
            "Kiosk@123",
            "9000000006",
        )

        volunteer = create_user(
            db,
            "SeniorSathi Volunteer",
            "volunteer@digidarshan.in",
            UserRole.senior_sathi_volunteer,
            "Volunteer@123",
            "9000000007",
        )

        vip = create_user(
            db,
            "VIP Coordinator",
            "vip@digidarshan.in",
            UserRole.vip_coordinator,
            "Vip@123",
            "9000000008",
        )

        somnath = create_temple(
            db,
            "Somnath Temple",
            "Somnath",
            "SOM",
            10000,
            7000,
            1800,
            4,
            4,
        )

        dwarka = create_temple(
            db,
            "Dwarkadhish Temple",
            "Dwarka",
            "DWA",
            8000,
            5500,
            1200,
            3,
            3,
        )

        ambaji = create_temple(
            db,
            "Ambaji Temple",
            "Ambaji",
            "AMB",
            9000,
            6000,
            1500,
            4,
            4,
        )

        pavagadh = create_temple(
            db,
            "Pavagadh Kalika Mata Temple",
            "Pavagadh",
            "PAV",
            7000,
            4500,
            900,
            3,
            3,
        )

        temples = [somnath, dwarka, ambaji, pavagadh]

        for temple in temples:
            create_slots(db, temple)
            create_parking(db, temple)
            create_transport(db, temple)
            create_initial_crowd(db, temple)

            assign_staff(db, scanner, temple, UserRole.scanner, "Gate Scanning", "Gate A")
            assign_staff(db, operator, temple, UserRole.emergency_operator, "Control Room")
            assign_staff(db, kiosk, temple, UserRole.kiosk_operator, "Helpdesk")
            assign_staff(db, volunteer, temple, UserRole.senior_sathi_volunteer, "SeniorSathi")
            assign_staff(db, vip, temple, UserRole.vip_coordinator, "VIP Movement")

        create_demo_booking(db, pilgrim, somnath)
        create_alert(db, somnath, admin)

        print("Seed completed successfully.")
        print("")
        print("Demo logins:")
        print("admin@digidarshan.in / Admin@123")
        print("superadmin@digidarshan.in / Super@123")
        print("pilgrim@digidarshan.in / Pilgrim@123")
        print("scanner@digidarshan.in / Scanner@123")
        print("operator@digidarshan.in / Operator@123")
        print("kiosk@digidarshan.in / Kiosk@123")
        print("volunteer@digidarshan.in / Volunteer@123")
        print("vip@digidarshan.in / Vip@123")

    finally:
        db.close()


if __name__ == "__main__":
    seed()