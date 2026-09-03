"""Reference API test: happy path, business rule, failure case."""

from fastapi.testclient import TestClient

PAYLOAD = {
    "first_name": "Ana",
    "last_name": "Garcia",
    "email": "ana.garcia@example.org",
    "is_specialist": False,
    "max_periods_per_week": 25,
    "active": True,
}


def test_creates_and_lists_a_teacher(client: TestClient) -> None:
    response = client.post("/api/v1/teachers", json=PAYLOAD)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] > 0
    assert created["email"] == PAYLOAD["email"]

    listed = client.get("/api/v1/teachers").json()
    assert [teacher["id"] for teacher in listed] == [created["id"]]


def test_rejects_a_duplicate_email(client: TestClient) -> None:
    client.post("/api/v1/teachers", json=PAYLOAD)
    response = client.post("/api/v1/teachers", json=PAYLOAD)
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_returns_404_for_an_unknown_teacher(client: TestClient) -> None:
    response = client.get("/api/v1/teachers/999")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_updates_only_the_given_fields(client: TestClient) -> None:
    teacher_id = client.post("/api/v1/teachers", json=PAYLOAD).json()["id"]
    response = client.patch(f"/api/v1/teachers/{teacher_id}", json={"is_specialist": True})
    assert response.status_code == 200
    updated = response.json()
    assert updated["is_specialist"] is True
    assert updated["last_name"] == PAYLOAD["last_name"]
