from datetime import datetime, timedelta, timezone

from app.database import Base, SessionLocal, engine
from app.models import ParkingZone, Temple, TimeSlot, TransportRoute, User, UserRole
from app.security import get_password_hash

Base.metadata.create_all(bind=engine)


def create_user(db, name, email, role, password="Password@123", phone=None):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(
        name=name,
        email=email,
        phone=phone,
        role=role,
        password_hash=get_password_hash(password),
    )
    db.add(user)
    db.commit()
    return user


def create_temple(db, **kwargs):
    temple = db.query(Temple).filter(Temple.name == kwargs["name"]).first()
    if temple:
        return temple
    temple = Temple(**kwargs)
    db.add(temple)
    db.commit()
    db.refresh(temple)
    return temple


def seed():
    db = SessionLocal()
    try:
        create_user(db, "System Admin", "admin@digidarshan.in", UserRole.admin, "Admin@123")
        create_user(db, "Emergency Operator", "operator@digidarshan.in", UserRole.emergency_operator, "Operator@123")
        create_user(db, "Gate Scanner", "scanner@digidarshan.in", UserRole.scanner, "Scanner@123")
        create_user(db, "Demo Pilgrim", "pilgrim@digidarshan.in", UserRole.pilgrim, "Pilgrim@123", "9999999999")

        temples = [
            create_temple(
                db,
                name="Somnath Temple",
                city="Somnath",
                description="Live queue and crowd safety management for Somnath pilgrimage visitors.",
                latitude=20.888,
                longitude=70.401,
                max_capacity=8000,
                current_occupancy=2100,
                entry_gates=4,
                exit_gates=3,
                emergency_contact="108",
            ),
            create_temple(
                db,
                name="Dwarkadhish Temple",
                city="Dwarka",
                description="Slot-based darshan, parking, and transport coordination for Dwarka.",
                latitude=22.239,
                longitude=68.967,
                max_capacity=6500,
                current_occupancy=1800,
                entry_gates=3,
                exit_gates=3,
                emergency_contact="108",
            ),
            create_temple(
                db,
                name="Ambaji Temple",
                city="Ambaji",
                description="SeniorSathi priority windows and festival crowd regulation for Ambaji.",
                latitude=24.331,
                longitude=72.851,
                max_capacity=7000,
                current_occupancy=2600,
                entry_gates=4,
                exit_gates=4,
                emergency_contact="108",
            ),
            create_temple(
                db,
                name="Pavagadh Kalika Mata Temple",
                city="Pavagadh",
                description="Route guidance, queue heat tracking, and emergency alerts for Pavagadh.",
                latitude=22.466,
                longitude=73.503,
                max_capacity=5000,
                current_occupancy=1200,
                entry_gates=2,
                exit_gates=2,
                emergency_contact="108",
            ),
        ]

        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        for temple in temples:
            if not db.query(TimeSlot).filter(TimeSlot.temple_id == temple.id).first():
                for day in range(0, 5):
                    for hour in [7, 9, 11, 15, 17, 19]:
                        start = (now + timedelta(days=day)).replace(hour=hour)
                        end = start + timedelta(hours=1)
                        capacity = 250 if hour in [7, 15] else 350
                        db.add(
                            TimeSlot(
                                temple_id=temple.id,
                                start_time=start,
                                end_time=end,
                                capacity=capacity,
                                senior_reserved_capacity=40,
                            )
                        )
            if not db.query(ParkingZone).filter(ParkingZone.temple_id == temple.id).first():
                db.add_all(
                    [
                        ParkingZone(
                            temple_id=temple.id,
                            name="North Parking",
                            total_slots=300,
                            available_slots=180,
                            distance_label="450 m from main gate",
                            route_hint="Use Gate A pedestrian corridor.",
                        ),
                        ParkingZone(
                            temple_id=temple.id,
                            name="Shuttle Parking",
                            total_slots=600,
                            available_slots=420,
                            distance_label="1.8 km with shuttle",
                            route_hint="Board free shuttle every 10 minutes.",
                        ),
                    ]
                )
            if not db.query(TransportRoute).filter(TransportRoute.temple_id == temple.id).first():
                db.add_all(
                    [
                        TransportRoute(
                            temple_id=temple.id,
                            name="Station Shuttle",
                            mode="shuttle",
                            start_point="Railway/Bus Station",
                            end_point="Temple Gate A",
                            frequency_minutes=15,
                            status="On time",
                            notes="Recommended during peak hours.",
                        ),
                        TransportRoute(
                            temple_id=temple.id,
                            name="Emergency Corridor",
                            mode="emergency",
                            start_point="Medical Camp",
                            end_point="Emergency Gate",
                            frequency_minutes=5,
                            status="Clear",
                            notes="Reserved for police, ambulance, and rescue teams.",
                        ),
                    ]
                )
        db.commit()
        print("Seed completed")
        print("Admin: admin@digidarshan.in / Admin@123")
        print("Operator: operator@digidarshan.in / Operator@123")
        print("Scanner: scanner@digidarshan.in / Scanner@123")
        print("Pilgrim: pilgrim@digidarshan.in / Pilgrim@123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
