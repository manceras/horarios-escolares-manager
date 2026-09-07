"""Create the database schema and a realistic data set for development.

The shape mirrors a small Spanish primary school: one group per grade, tutors who
teach most of their own group's subjects, and specialists who rotate across every
group for English, PE, music and religion. That rotation is what makes timetabling
hard, so a seed without it would not exercise the solver at all.

Idempotent: running it twice leaves the same data. Never run it against real data.
"""

from datetime import time

from app.core.db import SessionLocal, engine
from app.models import (
    Base,
    ClassGroup,
    CurriculumEntry,
    Room,
    RoomType,
    Subject,
    Teacher,
    TeacherUnavailability,
    TimeSlot,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# start, end, is_break
PERIODS = [
    (time(9, 0), time(9, 45), False),
    (time(9, 45), time(10, 30), False),
    (time(10, 30), time(11, 15), False),
    (time(11, 15), time(11, 45), True),  # recreo
    (time(11, 45), time(12, 30), False),
    (time(12, 30), time(13, 15), False),
]

# code, name, required room type, periods per week, taught by a specialist
SUBJECTS = [
    ("LEN", "Lengua Castellana", None, 5, False),
    ("MAT", "Matemáticas", None, 5, False),
    ("CNA", "Conocimiento del Medio Natural", None, 2, False),
    ("CSO", "Conocimiento del Medio Social", None, 2, False),
    ("ART", "Educación Plástica", None, 1, False),
    ("ING", "Inglés", None, 3, True),
    ("EF", "Educación Física", RoomType.GYM, 2, True),
    ("MUS", "Música", RoomType.MUSIC, 1, True),
    ("REL", "Religión y Valores", None, 1, True),
]

# first name, last name, subject codes they cover across every group
SPECIALISTS = [
    ("Luis", "Pérez", ["ING"]),
    ("Marta", "Ruiz", ["EF"]),
    ("Javier", "Ortega", ["MUS", "REL"]),
]

TUTORS = [
    ("Ana", "García"),
    ("Carmen", "López"),
    (
        "David",
        "Sánchez",
    ),
    ("Elena", "Martín"),
    ("Sergio", "Navarro"),
    ("Lucía", "Romero"),
]


def _email(first_name: str, last_name: str) -> str:
    normalised = (
        f"{first_name}.{last_name}".lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    return f"{normalised}@example.org"


def seed(session: Session) -> None:
    if session.scalar(select(func.count()).select_from(Teacher)):
        print("Database already seeded, nothing to do")
        return

    slots = [
        TimeSlot(
            day_of_week=day,
            period_index=index,
            start_time=start,
            end_time=end,
            is_break=is_break,
        )
        for day in range(5)
        for index, (start, end, is_break) in enumerate(PERIODS)
    ]
    session.add_all(slots)

    classrooms = [
        Room(name=f"Aula {grade}º", room_type=RoomType.CLASSROOM, capacity=25)
        for grade in range(1, 7)
    ]
    special_rooms = [
        Room(name="Gimnasio", room_type=RoomType.GYM, capacity=60),
        Room(name="Aula de Música", room_type=RoomType.MUSIC, capacity=30),
        Room(name="Aula de Informática", room_type=RoomType.COMPUTER_LAB, capacity=25),
    ]
    session.add_all(classrooms + special_rooms)

    subjects = {
        code: Subject(code=code, name=name, required_room_type=room_type)
        for code, name, room_type, _, _ in SUBJECTS
    }
    session.add_all(subjects.values())

    tutors = [
        Teacher(
            first_name=first_name,
            last_name=last_name,
            email=_email(first_name, last_name),
            is_specialist=False,
            max_periods_per_week=25,
        )
        for first_name, last_name in TUTORS
    ]
    specialists = {
        last_name: Teacher(
            first_name=first_name,
            last_name=last_name,
            email=_email(first_name, last_name),
            is_specialist=True,
            max_periods_per_week=25,
        )
        for first_name, last_name, _ in SPECIALISTS
    }
    session.add_all(tutors + list(specialists.values()))
    session.flush()

    specialist_by_subject = {
        code: specialists[last_name] for _, last_name, codes in SPECIALISTS for code in codes
    }

    groups = [
        ClassGroup(
            name=f"{grade}A",
            grade=grade,
            tutor_id=tutors[grade - 1].id,
            home_room_id=classrooms[grade - 1].id,
        )
        for grade in range(1, 7)
    ]
    session.add_all(groups)
    session.flush()

    for group, tutor in zip(groups, tutors, strict=True):
        for code, _, _, periods, needs_specialist in SUBJECTS:
            teacher = specialist_by_subject[code] if needs_specialist else tutor
            session.add(
                CurriculumEntry(
                    class_group_id=group.id,
                    subject_id=subjects[code].id,
                    teacher_id=teacher.id,
                    periods_per_week=periods,
                )
            )

    # The music and religion specialist only comes in three days a week. This is
    # the constraint that makes a hand-made timetable painful, so the development
    # data should contain it.
    part_time = specialists["Ortega"]
    session.add_all(
        TeacherUnavailability(
            teacher_id=part_time.id,
            time_slot_id=slot.id,
            reason="Jornada parcial",
        )
        for slot in slots
        if slot.day_of_week in (0, 4) and not slot.is_break
    )

    print(
        f"Seeded {len(groups)} class groups, {len(tutors) + len(specialists)} teachers, "
        f"{len(subjects)} subjects and {len(groups) * len(SUBJECTS)} curriculum entries"
    )


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as db_session:
        seed(db_session)
