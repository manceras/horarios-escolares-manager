"""Room API tests: happy path, business rules, failure cases."""

from datetime import time

from app.models.curriculum import CurriculumEntry
from app.models.enums import RoomType
from app.models.schedule import Schedule, ScheduledSession
from app.models.school import ClassGroup, Room, Teacher, TimeSlot
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

PAYLOAD = {
    "name": "Classroom 1A",
    "room_type": "classroom",
    "capacity": 25,
}


def test_creates_and_lists_a_room(client: TestClient) -> None:
    response = client.post("/api/v1/rooms", json=PAYLOAD)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] > 0
    assert created["name"] == PAYLOAD["name"]

    listed = client.get("/api/v1/rooms").json()
    assert [room["id"] for room in listed] == [created["id"]]


def test_rejects_a_duplicate_name(client: TestClient) -> None:
    client.post("/api/v1/rooms", json=PAYLOAD)
    response = client.post("/api/v1/rooms", json=PAYLOAD)
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_returns_404_for_an_unknown_room(client: TestClient) -> None:
    response = client.get("/api/v1/rooms/999")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_updates_only_the_given_fields(client: TestClient) -> None:
    room_id = client.post("/api/v1/rooms", json=PAYLOAD).json()["id"]
    response = client.patch(f"/api/v1/rooms/{room_id}", json={"capacity": 30})
    assert response.status_code == 200
    updated = response.json()
    assert updated["capacity"] == 30
    assert updated["name"] == PAYLOAD["name"]


def test_deletes_an_unreferenced_room(client: TestClient) -> None:
    room_id = client.post("/api/v1/rooms", json=PAYLOAD).json()["id"]
    response = client.delete(f"/api/v1/rooms/{room_id}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/rooms/{room_id}").status_code == 404


def test_rejects_deleting_a_room_used_as_a_class_group_home_room(
    client: TestClient, session: Session
) -> None:
    room_id = client.post("/api/v1/rooms", json=PAYLOAD).json()["id"]
    group = ClassGroup(name="3A", grade=3, home_room_id=room_id)
    session.add(group)
    session.commit()

    response = client.delete(f"/api/v1/rooms/{room_id}")
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_rejects_deleting_a_room_used_by_a_scheduled_session(
    client: TestClient, session: Session
) -> None:
    room_id = client.post("/api/v1/rooms", json=PAYLOAD).json()["id"]
    other_room = Room(name="Gym", room_type=RoomType.GYM, capacity=40)
    time_slot = TimeSlot(day_of_week=0, period_index=0, start_time=time(9, 0), end_time=time(9, 45))
    schedule = Schedule(name="Draft")
    session.add_all([other_room, time_slot, schedule])
    session.commit()

    subject_id = client.post(
        "/api/v1/subjects", json={"code": "PE", "name": "Physical Education"}
    ).json()["id"]

    teacher = Teacher(first_name="Ana", last_name="Garcia", email="ana.garcia@example.org")
    group = ClassGroup(name="4B", grade=4, home_room_id=other_room.id)
    session.add_all([teacher, group])
    session.commit()

    entry = CurriculumEntry(
        class_group_id=group.id, subject_id=subject_id, teacher_id=teacher.id, periods_per_week=2
    )
    session.add(entry)
    session.commit()

    scheduled_session = ScheduledSession(
        schedule_id=schedule.id,
        curriculum_entry_id=entry.id,
        time_slot_id=time_slot.id,
        room_id=room_id,
    )
    session.add(scheduled_session)
    session.commit()

    response = client.delete(f"/api/v1/rooms/{room_id}")
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
