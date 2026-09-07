"""TeacherUnavailability API tests: happy path, business rules, failure cases."""

from datetime import time

import pytest
from app.models.school import Teacher, TimeSlot
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def teacher_a(session: Session) -> Teacher:
    teacher = Teacher(first_name="Ana", last_name="Garcia", email="ana@example.org")
    session.add(teacher)
    session.commit()
    return teacher


@pytest.fixture
def teacher_b(session: Session) -> Teacher:
    teacher = Teacher(first_name="Bea", last_name="Lopez", email="bea@example.org")
    session.add(teacher)
    session.commit()
    return teacher


@pytest.fixture
def slots(session: Session) -> list[TimeSlot]:
    monday = TimeSlot(day_of_week=0, period_index=0, start_time=time(9, 0), end_time=time(9, 45))
    tuesday = TimeSlot(day_of_week=1, period_index=0, start_time=time(9, 0), end_time=time(9, 45))
    session.add_all([monday, tuesday])
    session.commit()
    return [monday, tuesday]


def test_creates_and_lists_an_unavailability(
    client: TestClient, teacher_a: Teacher, slots: list[TimeSlot]
) -> None:
    response = client.post(
        "/api/v1/teacher-unavailabilities",
        json={"teacher_id": teacher_a.id, "time_slot_id": slots[0].id},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["teacher_id"] == teacher_a.id

    listed = client.get(
        "/api/v1/teacher-unavailabilities", params={"teacher_id": teacher_a.id}
    ).json()
    assert [row["id"] for row in listed] == [created["id"]]


def test_rejects_a_duplicate_teacher_and_slot(
    client: TestClient, teacher_a: Teacher, slots: list[TimeSlot]
) -> None:
    payload = {"teacher_id": teacher_a.id, "time_slot_id": slots[0].id}
    client.post("/api/v1/teacher-unavailabilities", json=payload)
    response = client.post("/api/v1/teacher-unavailabilities", json=payload)
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_rejects_an_unknown_teacher(client: TestClient, slots: list[TimeSlot]) -> None:
    response = client.post(
        "/api/v1/teacher-unavailabilities", json={"teacher_id": 999, "time_slot_id": slots[0].id}
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_rejects_an_unknown_time_slot(client: TestClient, teacher_a: Teacher) -> None:
    response = client.post(
        "/api/v1/teacher-unavailabilities", json={"teacher_id": teacher_a.id, "time_slot_id": 999}
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_deletes_an_unavailability(
    client: TestClient, teacher_a: Teacher, slots: list[TimeSlot]
) -> None:
    row_id = client.post(
        "/api/v1/teacher-unavailabilities",
        json={"teacher_id": teacher_a.id, "time_slot_id": slots[0].id},
    ).json()["id"]
    response = client.delete(f"/api/v1/teacher-unavailabilities/{row_id}")
    assert response.status_code == 204
    assert client.get("/api/v1/teacher-unavailabilities").json() == []


def test_replaces_the_full_set_for_a_teacher(
    client: TestClient, teacher_a: Teacher, slots: list[TimeSlot]
) -> None:
    client.post(
        "/api/v1/teacher-unavailabilities",
        json={"teacher_id": teacher_a.id, "time_slot_id": slots[0].id},
    )

    response = client.put(
        f"/api/v1/teacher-unavailabilities/teacher/{teacher_a.id}",
        json={"time_slot_ids": [slots[1].id]},
    )
    assert response.status_code == 200
    replaced = response.json()
    assert [row["time_slot_id"] for row in replaced] == [slots[1].id]

    listed = client.get(
        "/api/v1/teacher-unavailabilities", params={"teacher_id": teacher_a.id}
    ).json()
    assert [row["time_slot_id"] for row in listed] == [slots[1].id]
