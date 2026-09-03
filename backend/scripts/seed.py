"""Create the database schema and a minimal, realistic data set for development.

Idempotent: running it twice leaves the same data. Never run it against real data.
"""

from datetime import time

from app.core.db import SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    Base,
    ClassGroup,
    CurriculumEntry,
    Room,
    RoomType,
    Subject,
    Teacher,
    TimeSlot,
    User,
    UserRole,
)
from sqlalchemy.orm import Session

PERIODS = [
    (time(9, 0), time(9, 45), False),
    (time(9, 45), time(10, 30), False),
    (time(10, 30), time(11, 15), False),
    (time(11, 15), time(11, 45), True),  # recreo
    (time(11, 45), time(12, 30), False),
    (time(12, 30), time(13, 15), False),
]


def seed(session: Session) -> None:
    if session.query(Teacher).count() > 0:
        print("Database already seeded, nothing to do")
        return

    for day in range(5):
        for index, (start, end, is_break) in enumerate(PERIODS):
            session.add(
                TimeSlot(
                    day_of_week=day,
                    period_index=index,
                    start_time=start,
                    end_time=end,
                    is_break=is_break,
                )
            )

    classroom_3a = Room(name="Aula 3A", room_type=RoomType.CLASSROOM, capacity=25)
    gym = Room(name="Gimnasio", room_type=RoomType.GYM, capacity=60)
    session.add_all([classroom_3a, gym])

    maths = Subject(code="MAT", name="Matemáticas")
    spanish = Subject(code="LEN", name="Lengua Castellana")
    pe = Subject(code="EF", name="Educación Física", required_room_type=RoomType.GYM)
    session.add_all([maths, spanish, pe])

    tutor = Teacher(
        first_name="Ana", last_name="García", email="ana.garcia@example.org", is_specialist=False
    )
    pe_teacher = Teacher(
        first_name="Luis", last_name="Pérez", email="luis.perez@example.org", is_specialist=True
    )
    session.add_all([tutor, pe_teacher])
    session.flush()

    group = ClassGroup(name="3A", grade=3, tutor_id=tutor.id, home_room_id=classroom_3a.id)
    session.add(group)
    session.flush()

    session.add_all(
        [
            CurriculumEntry(
                class_group_id=group.id,
                subject_id=maths.id,
                teacher_id=tutor.id,
                periods_per_week=5,
            ),
            CurriculumEntry(
                class_group_id=group.id,
                subject_id=spanish.id,
                teacher_id=tutor.id,
                periods_per_week=5,
            ),
            CurriculumEntry(
                class_group_id=group.id,
                subject_id=pe.id,
                teacher_id=pe_teacher.id,
                periods_per_week=2,
            ),
        ]
    )

    session.add(
        User(
            email="admin@example.org",
            hashed_password=hash_password("changeme"),
            role=UserRole.ADMIN,
        )
    )
    session.commit()
    print("Seeded development data (admin@example.org / changeme)")


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as db_session:
        seed(db_session)
