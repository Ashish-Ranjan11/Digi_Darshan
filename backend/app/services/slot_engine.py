from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models import Temple, TimeSlot


def generate_daily_slots_for_temple(
    db: Session,
    temple_id: int,
    days_ahead: int = 7,
    start_hour: int = 6,
    end_hour: int = 18,
    capacity: int = 300,
    senior_reserved_capacity: int = 40,
) -> int:
    created_count = 0
    today = datetime.now().date()

    for day_offset in range(days_ahead):
        target_date = today + timedelta(days=day_offset)

        for hour in range(start_hour, end_hour):
            start_time = datetime.combine(target_date, time(hour, 0))
            end_time = start_time + timedelta(hours=1)

            existing = (
                db.query(TimeSlot)
                .filter(TimeSlot.temple_id == temple_id)
                .filter(TimeSlot.start_time == start_time)
                .filter(TimeSlot.end_time == end_time)
                .first()
            )

            if existing:
                continue

            slot = TimeSlot(
                temple_id=temple_id,
                start_time=start_time,
                end_time=end_time,
                capacity=capacity,
                booked_count=0,
                senior_reserved_capacity=senior_reserved_capacity,
                is_active=True,
            )

            db.add(slot)
            created_count += 1

    db.commit()
    return created_count


def generate_daily_slots_for_all_temples(
    db: Session,
    days_ahead: int = 7,
    capacity: int = 300,
) -> int:
    temples = db.query(Temple).filter(Temple.is_active.is_(True)).all()
    total_created = 0

    for temple in temples:
        total_created += generate_daily_slots_for_temple(
            db=db,
            temple_id=temple.id,
            days_ahead=days_ahead,
            start_hour=6,
            end_hour=18,
            capacity=capacity,
            senior_reserved_capacity=40,
        )

    return total_created