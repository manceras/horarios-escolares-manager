"""TimeSlot API tests: happy path, business rules, failure cases."""

from app.models.curriculum import CurriculumEntry
from app.models.schedule import Schedule, ScheduledSession
from app.models.school import ClassGroup, Subject, Teacher
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

PAYLOAD = {
    "day_of_week": 0,
    "period_index": 0,
    "start_time": "09:00:00",
    "end_time": "09:45:00",
    "is_break": False,
}


def test_creates_and_lists_a_time_slot(client: TestClient) -> None:
    response = client.post("/api/v1/time-slots", json=PAYLOAD)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] > 0
    assert created["day_of_week"] == 0

    listed = client.get("/api/v1/time-slots").json()
    assert [slot["id"] for slot in listed] == [created["id"]]


def test_rejects_a_duplicate_day_and_period(client: TestClient) -> None:
    client.post("/api/v1/time-slots", json=PAYLOAD)
    response = client.post(
        "/api/v1/time-slots", json={**PAYLOAD, "start_time": "10:00:00", "end_time": "10:45:00"}
    )
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_rejects_a_day_of_week_outside_monday_to_friday(client: TestClient) -> None:
    response = client.post("/api/v1/time-slots", json={**PAYLOAD, "day_of_week": 5})
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


def test_rejects_a_start_time_not_before_end_time(client: TestClient) -> None:
    response = client.post(
        "/api/v1/time-slots", json={**PAYLOAD, "start_time": "10:00:00", "end_time": "09:00:00"}
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


def test_returns_404_for_an_unknown_time_slot(client: TestClient) -> None:
    response = client.get("/api/v1/time-slots/999")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_updates_only_the_given_fields(client: TestClient) -> None:
    slot_id = client.post("/api/v1/time-slots", json=PAYLOAD).json()["id"]
    response = client.patch(f"/api/v1/time-slots/{slot_id}", json={"is_break": True})
    assert response.status_code == 200
    updated = response.json()
    assert updated["is_break"] is True
    assert updated["day_of_week"] == PAYLOAD["day_of_week"]


def test_deletes_a_time_slot(client: TestClient) -> None:
    slot_id = client.post("/api/v1/time-slots", json=PAYLOAD).json()["id"]
    response = client.delete(f"/api/v1/time-slots/{slot_id}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/time-slots/{slot_id}").status_code == 404


def test_rejects_deleting_a_time_slot_referenced_by_a_scheduled_session(
    client: TestClient, session: Session
) -> None:
    slot_id = client.post("/api/v1/time-slots", json=PAYLOAD).json()["id"]

    teacher = Teacher(first_name="Ana", last_name="Garcia", email="ana@example.org")
    subject = Subject(code="MAT", name="Maths")
    group = ClassGroup(name="3A", grade=3)
    session.add_all([teacher, subject, group])
    session.commit()

    entry = CurriculumEntry(
        class_group_id=group.id, subject_id=subject.id, teacher_id=teacher.id, periods_per_week=4
    )
    session.add(entry)
    session.commit()

    schedule = Schedule(name="Draft")
    session.add(schedule)
    session.commit()
    session.add(
        ScheduledSession(
            schedule_id=schedule.id, curriculum_entry_id=entry.id, time_slot_id=slot_id
        )
    )
    session.commit()

    response = client.delete(f"/api/v1/time-slots/{slot_id}")
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
