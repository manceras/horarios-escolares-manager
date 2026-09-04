"""Curriculum entry tests: happy path, every business rule, and failure cases.

There is no router for ClassGroup, Subject or TimeSlot yet, so prerequisite
rows are inserted directly through the ``session`` fixture and exercised
through the API client, which shares that same session.
"""

from datetime import time

from app.models.curriculum import CurriculumEntry
from app.models.schedule import Schedule, ScheduledSession
from app.models.school import ClassGroup, Subject, Teacher, TimeSlot
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

_next_id = 0


def _unique_suffix() -> int:
    global _next_id
    _next_id += 1
    return _next_id


def make_teacher(session: Session, *, max_periods_per_week: int = 25) -> Teacher:
    suffix = _unique_suffix()
    teacher = Teacher(
        first_name="Ana",
        last_name=f"Garcia{suffix}",
        email=f"ana.garcia{suffix}@example.org",
        max_periods_per_week=max_periods_per_week,
    )
    session.add(teacher)
    session.commit()
    return teacher


def make_class_group(session: Session) -> ClassGroup:
    suffix = _unique_suffix()
    group = ClassGroup(name=f"3A{suffix}", grade=3)
    session.add(group)
    session.commit()
    return group


def make_subject(session: Session) -> Subject:
    suffix = _unique_suffix()
    subject = Subject(code=f"MAT{suffix}", name=f"Mathematics {suffix}")
    session.add(subject)
    session.commit()
    return subject


def make_time_slot(
    session: Session, *, day_of_week: int, period_index: int, is_break: bool = False
) -> TimeSlot:
    slot = TimeSlot(
        day_of_week=day_of_week,
        period_index=period_index,
        start_time=time(9, 0),
        end_time=time(9, 45),
        is_break=is_break,
    )
    session.add(slot)
    session.commit()
    return slot


def make_entry_payload(
    class_group: ClassGroup, subject: Subject, teacher: Teacher, periods: int = 2
) -> dict:
    return {
        "class_group_id": class_group.id,
        "subject_id": subject.id,
        "teacher_id": teacher.id,
        "periods_per_week": periods,
    }


def test_creates_and_lists_a_curriculum_entry(client: TestClient, session: Session) -> None:
    teacher = make_teacher(session)
    group = make_class_group(session)
    subject = make_subject(session)
    make_time_slot(session, day_of_week=0, period_index=0)
    make_time_slot(session, day_of_week=0, period_index=1)

    response = client.post(
        "/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher)
    )
    assert response.status_code == 201
    created = response.json()
    assert created["id"] > 0
    assert created["periods_per_week"] == 2

    listed = client.get("/api/v1/curriculum-entries").json()
    assert len(listed) == 1
    detail = listed[0]
    assert detail["id"] == created["id"]
    assert detail["class_group_name"] == group.name
    assert detail["subject_code"] == subject.code
    assert detail["subject_name"] == subject.name
    assert detail["teacher_name"] == teacher.full_name

    fetched = client.get(f"/api/v1/curriculum-entries/{created['id']}").json()
    assert fetched["class_group_name"] == group.name


def test_rejects_a_duplicate_group_subject_pair(client: TestClient, session: Session) -> None:
    teacher = make_teacher(session)
    other_teacher = make_teacher(session)
    group = make_class_group(session)
    subject = make_subject(session)
    for i in range(2):
        make_time_slot(session, day_of_week=0, period_index=i)

    client.post("/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher, 1))
    response = client.post(
        "/api/v1/curriculum-entries", json=make_entry_payload(group, subject, other_teacher, 1)
    )
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_rejects_an_unknown_class_group(client: TestClient, session: Session) -> None:
    teacher = make_teacher(session)
    subject = make_subject(session)
    response = client.post(
        "/api/v1/curriculum-entries",
        json={
            "class_group_id": 999,
            "subject_id": subject.id,
            "teacher_id": teacher.id,
            "periods_per_week": 1,
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_rejects_an_unknown_subject(client: TestClient, session: Session) -> None:
    teacher = make_teacher(session)
    group = make_class_group(session)
    response = client.post(
        "/api/v1/curriculum-entries",
        json={
            "class_group_id": group.id,
            "subject_id": 999,
            "teacher_id": teacher.id,
            "periods_per_week": 1,
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_rejects_an_unknown_teacher(client: TestClient, session: Session) -> None:
    group = make_class_group(session)
    subject = make_subject(session)
    response = client.post(
        "/api/v1/curriculum-entries",
        json={
            "class_group_id": group.id,
            "subject_id": subject.id,
            "teacher_id": 999,
            "periods_per_week": 1,
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_rejects_zero_periods_per_week(client: TestClient, session: Session) -> None:
    teacher = make_teacher(session)
    group = make_class_group(session)
    subject = make_subject(session)
    response = client.post(
        "/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher, 0)
    )
    assert response.status_code == 422


def test_rejects_entry_exceeding_group_available_slots(
    client: TestClient, session: Session
) -> None:
    teacher = make_teacher(session)
    group = make_class_group(session)
    subject = make_subject(session)
    # Only one non-break slot is available for the group.
    make_time_slot(session, day_of_week=0, period_index=0)

    response = client.post(
        "/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher, 2)
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert group.name in detail
    assert "2" in detail
    assert "1" in detail


def test_rejects_entry_exceeding_teacher_max_periods(client: TestClient, session: Session) -> None:
    teacher = make_teacher(session, max_periods_per_week=1)
    group = make_class_group(session)
    subject = make_subject(session)
    for i in range(2):
        make_time_slot(session, day_of_week=0, period_index=i)

    response = client.post(
        "/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher, 2)
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert teacher.full_name in detail
    assert "2" in detail
    assert "1" in detail


def test_rejects_deleting_an_entry_with_scheduled_sessions(
    client: TestClient, session: Session
) -> None:
    teacher = make_teacher(session)
    group = make_class_group(session)
    subject = make_subject(session)
    slot = make_time_slot(session, day_of_week=0, period_index=0)
    make_time_slot(session, day_of_week=0, period_index=1)

    entry_id = client.post(
        "/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher, 1)
    ).json()["id"]

    entry = session.get(CurriculumEntry, entry_id)
    assert entry is not None
    schedule = Schedule(name="Draft")
    session.add(schedule)
    session.commit()
    session.add(
        ScheduledSession(
            schedule_id=schedule.id, curriculum_entry_id=entry.id, time_slot_id=slot.id
        )
    )
    session.commit()

    response = client.delete(f"/api/v1/curriculum-entries/{entry_id}")
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_deletes_an_entry_without_scheduled_sessions(client: TestClient, session: Session) -> None:
    teacher = make_teacher(session)
    group = make_class_group(session)
    subject = make_subject(session)
    make_time_slot(session, day_of_week=0, period_index=0)

    entry_id = client.post(
        "/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher, 1)
    ).json()["id"]

    response = client.delete(f"/api/v1/curriculum-entries/{entry_id}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/curriculum-entries/{entry_id}").status_code == 404


def test_returns_404_for_an_unknown_curriculum_entry(client: TestClient) -> None:
    response = client.get("/api/v1/curriculum-entries/999")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_updates_only_the_given_fields(client: TestClient, session: Session) -> None:
    teacher = make_teacher(session)
    group = make_class_group(session)
    subject = make_subject(session)
    for i in range(3):
        make_time_slot(session, day_of_week=0, period_index=i)

    entry_id = client.post(
        "/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher, 2)
    ).json()["id"]

    response = client.patch(f"/api/v1/curriculum-entries/{entry_id}", json={"periods_per_week": 3})
    assert response.status_code == 200
    updated = response.json()
    assert updated["periods_per_week"] == 3
    assert updated["teacher_id"] == teacher.id


def test_update_rejects_exceeding_group_available_slots(
    client: TestClient, session: Session
) -> None:
    teacher = make_teacher(session)
    group = make_class_group(session)
    subject = make_subject(session)
    for i in range(2):
        make_time_slot(session, day_of_week=0, period_index=i)

    entry_id = client.post(
        "/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher, 2)
    ).json()["id"]

    response = client.patch(f"/api/v1/curriculum-entries/{entry_id}", json={"periods_per_week": 3})
    assert response.status_code == 422
    assert group.name in response.json()["detail"]


def test_workload_reports_group_and_teacher_feasibility(
    client: TestClient, session: Session
) -> None:
    teacher = make_teacher(session, max_periods_per_week=3)
    group = make_class_group(session)
    subject = make_subject(session)
    make_time_slot(session, day_of_week=0, period_index=0)
    make_time_slot(session, day_of_week=0, period_index=1)
    make_time_slot(session, day_of_week=0, period_index=2, is_break=True)

    client.post("/api/v1/curriculum-entries", json=make_entry_payload(group, subject, teacher, 2))

    response = client.get("/api/v1/curriculum-entries/workload")
    assert response.status_code == 200
    body = response.json()

    group_row = next(row for row in body["groups"] if row["class_group_id"] == group.id)
    assert group_row["assigned_periods"] == 2
    assert group_row["available_periods"] == 2
    assert group_row["fits"] is True

    teacher_row = next(row for row in body["teachers"] if row["teacher_id"] == teacher.id)
    assert teacher_row["assigned_periods"] == 2
    assert teacher_row["max_periods_per_week"] == 3
    assert teacher_row["fits"] is True
