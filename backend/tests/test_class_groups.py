"""ClassGroup API tests: happy path, business rules, failure cases."""

from app.models.curriculum import CurriculumEntry
from app.models.school import Room, Subject, Teacher
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

PAYLOAD = {"name": "3A", "grade": 3}


def test_creates_and_lists_a_class_group(client: TestClient) -> None:
    response = client.post("/api/v1/class-groups", json=PAYLOAD)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] > 0
    assert created["name"] == PAYLOAD["name"]

    listed = client.get("/api/v1/class-groups").json()
    assert [group["id"] for group in listed] == [created["id"]]


def test_rejects_a_duplicate_name(client: TestClient) -> None:
    client.post("/api/v1/class-groups", json=PAYLOAD)
    response = client.post("/api/v1/class-groups", json=PAYLOAD)
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_rejects_a_grade_outside_one_to_six(client: TestClient) -> None:
    response = client.post("/api/v1/class-groups", json={"name": "9Z", "grade": 7})
    assert response.status_code == 422


def test_returns_404_for_an_unknown_class_group(client: TestClient) -> None:
    response = client.get("/api/v1/class-groups/999")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_rejects_an_unknown_tutor(client: TestClient) -> None:
    response = client.post("/api/v1/class-groups", json={**PAYLOAD, "tutor_id": 999})
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_rejects_an_unknown_home_room(client: TestClient) -> None:
    response = client.post("/api/v1/class-groups", json={**PAYLOAD, "home_room_id": 999})
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_creates_a_class_group_with_a_tutor_and_a_room(
    client: TestClient, session: Session
) -> None:
    teacher = Teacher(first_name="Ana", last_name="Garcia", email="ana@example.org")
    room = Room(name="Room 1")
    session.add_all([teacher, room])
    session.commit()

    response = client.post(
        "/api/v1/class-groups",
        json={**PAYLOAD, "tutor_id": teacher.id, "home_room_id": room.id},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["tutor_id"] == teacher.id
    assert created["home_room_id"] == room.id


def test_updates_only_the_given_fields(client: TestClient) -> None:
    group_id = client.post("/api/v1/class-groups", json=PAYLOAD).json()["id"]
    response = client.patch(f"/api/v1/class-groups/{group_id}", json={"grade": 4})
    assert response.status_code == 200
    updated = response.json()
    assert updated["grade"] == 4
    assert updated["name"] == PAYLOAD["name"]


def test_deletes_a_class_group(client: TestClient) -> None:
    group_id = client.post("/api/v1/class-groups", json=PAYLOAD).json()["id"]
    response = client.delete(f"/api/v1/class-groups/{group_id}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/class-groups/{group_id}").status_code == 404


def test_rejects_deleting_a_class_group_with_curriculum_entries(
    client: TestClient, session: Session
) -> None:
    group_id = client.post("/api/v1/class-groups", json=PAYLOAD).json()["id"]
    teacher = Teacher(first_name="Ana", last_name="Garcia", email="ana@example.org")
    subject = Subject(code="MAT", name="Maths")
    session.add_all([teacher, subject])
    session.commit()
    session.add(
        CurriculumEntry(
            class_group_id=group_id,
            subject_id=subject.id,
            teacher_id=teacher.id,
            periods_per_week=4,
        )
    )
    session.commit()

    response = client.delete(f"/api/v1/class-groups/{group_id}")
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
