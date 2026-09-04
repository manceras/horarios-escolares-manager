"""Subject API tests: happy path, business rules, failure cases."""

from app.models.curriculum import CurriculumEntry
from app.models.school import ClassGroup, Teacher
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

PAYLOAD = {
    "code": "MAT",
    "name": "Mathematics",
}


def test_creates_and_lists_a_subject(client: TestClient) -> None:
    response = client.post("/api/v1/subjects", json=PAYLOAD)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] > 0
    assert created["code"] == PAYLOAD["code"]

    listed = client.get("/api/v1/subjects").json()
    assert [subject["id"] for subject in listed] == [created["id"]]


def test_rejects_a_duplicate_code(client: TestClient) -> None:
    client.post("/api/v1/subjects", json=PAYLOAD)
    response = client.post("/api/v1/subjects", json=PAYLOAD)
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_returns_404_for_an_unknown_subject(client: TestClient) -> None:
    response = client.get("/api/v1/subjects/999")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_updates_only_the_given_fields(client: TestClient) -> None:
    subject_id = client.post("/api/v1/subjects", json=PAYLOAD).json()["id"]
    response = client.patch(f"/api/v1/subjects/{subject_id}", json={"name": "Applied Mathematics"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Applied Mathematics"
    assert updated["code"] == PAYLOAD["code"]


def test_accepts_a_valid_required_room_type(client: TestClient) -> None:
    payload = {**PAYLOAD, "code": "MUS", "required_room_type": "music"}
    response = client.post("/api/v1/subjects", json=payload)
    assert response.status_code == 201
    assert response.json()["required_room_type"] == "music"


def test_rejects_an_invalid_required_room_type(client: TestClient) -> None:
    payload = {**PAYLOAD, "code": "MUS", "required_room_type": "auditorium"}
    response = client.post("/api/v1/subjects", json=payload)
    assert response.status_code == 422


def test_allows_a_required_room_type_with_no_matching_room(client: TestClient) -> None:
    """A room type without a matching room yet is a data-entry ordering issue, not an error."""
    payload = {**PAYLOAD, "code": "COMP", "required_room_type": "computer_lab"}
    response = client.post("/api/v1/subjects", json=payload)
    assert response.status_code == 201
    assert response.json()["required_room_type"] == "computer_lab"


def test_deletes_an_unreferenced_subject(client: TestClient) -> None:
    subject_id = client.post("/api/v1/subjects", json=PAYLOAD).json()["id"]
    response = client.delete(f"/api/v1/subjects/{subject_id}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/subjects/{subject_id}").status_code == 404


def test_rejects_deleting_a_subject_used_by_a_curriculum_entry(
    client: TestClient, session: Session
) -> None:
    subject_id = client.post("/api/v1/subjects", json=PAYLOAD).json()["id"]
    teacher = Teacher(first_name="Ana", last_name="Garcia", email="ana.garcia@example.org")
    group = ClassGroup(name="3A", grade=3)
    session.add_all([teacher, group])
    session.commit()

    entry = CurriculumEntry(
        class_group_id=group.id, subject_id=subject_id, teacher_id=teacher.id, periods_per_week=4
    )
    session.add(entry)
    session.commit()

    response = client.delete(f"/api/v1/subjects/{subject_id}")
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
