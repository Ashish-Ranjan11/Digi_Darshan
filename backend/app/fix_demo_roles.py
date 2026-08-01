from sqlalchemy import func

from app.database import Base, engine, SessionLocal
from app.models import User, UserRole, Temple, TempleStaff
from app.security import get_password_hash


DEMO_USERS = [
    {
        "name": "Admin User",
        "email": "admin@digidarshan.in",
        "phone": "9000000001",
        "password": "Admin@123",
        "role": UserRole.admin,
    },
    {
        "name": "Super Admin",
        "email": "superadmin@digidarshan.in",
        "phone": "9000000002",
        "password": "Super@123",
        "role": UserRole.super_admin,
    },
    {
        "name": "Pilgrim User",
        "email": "pilgrim@digidarshan.in",
        "phone": "9000000003",
        "password": "Pilgrim@123",
        "role": UserRole.pilgrim,
    },
    {
        "name": "Scanner Staff",
        "email": "scanner@digidarshan.in",
        "phone": "9000000004",
        "password": "Scanner@123",
        "role": UserRole.scanner,
    },
    {
        "name": "Kiosk Operator",
        "email": "kiosk@digidarshan.in",
        "phone": "9000000005",
        "password": "Kiosk@123",
        "role": UserRole.kiosk_operator,
    },
    {
        "name": "SeniorSathi Volunteer",
        "email": "volunteer@digidarshan.in",
        "phone": "9000000006",
        "password": "Volunteer@123",
        "role": UserRole.senior_sathi_volunteer,
    },
    {
        "name": "VIP Coordinator",
        "email": "vip@digidarshan.in",
        "phone": "9000000007",
        "password": "Vip@123",
        "role": UserRole.vip_coordinator,
    },
    {
        "name": "Emergency Operator",
        "email": "emergency@digidarshan.in",
        "phone": "9000000008",
        "password": "Emergency@123",
        "role": UserRole.emergency_operator,
    },
]


def role_value(role):
    return role.value if hasattr(role, "value") else str(role)


def main():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        temples = db.query(Temple).all()

        for item in DEMO_USERS:
            email = item["email"].lower()

            user = db.query(User).filter(func.lower(User.email) == email).first()

            if not user:
                user = User(
                    name=item["name"],
                    email=email,
                    phone=item["phone"],
                    password_hash=get_password_hash(item["password"]),
                    role=item["role"],
                    is_active=True,
                )
                db.add(user)
                db.flush()
            else:
                user.name = item["name"]
                user.email = email
                user.phone = item["phone"]
                user.password_hash = get_password_hash(item["password"])
                user.role = item["role"]
                user.is_active = True
                db.flush()

            if item["role"] != UserRole.pilgrim and temples:
                existing_staff = (
                    db.query(TempleStaff)
                    .filter(TempleStaff.user_id == user.id)
                    .first()
                )

                if not existing_staff:
                    db.add(
                        TempleStaff(
                            user_id=user.id,
                            temple_id=temples[0].id,
                            role=role_value(item["role"]),
                            is_active=True,
                        )
                    )

        db.commit()

        print("\nDemo user roles fixed successfully:\n")

        users = db.query(User).order_by(User.id).all()

        for user in users:
            print(f"{user.email:<35} -> {role_value(user.role)}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
