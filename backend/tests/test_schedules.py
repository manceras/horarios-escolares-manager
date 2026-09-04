"""Schedule generation end to end: ORM data in, persisted timetable out.

The fixture school is deliberately tiny (one group, two teachers, twenty
teaching slots) so every test solves in well under a second.
"""

from collections.abc import Sequence
from datetime import time

import pytest
from app.models import (
    ClassGroup,
    CurriculumEntry,
    Room,
    RoomType,
    Schedule,
    ScheduledSession,
    ScheduleStatus,
    Subject,
    Teacher,
    TeacherUnavailability,
    TimeSlot,
)
from app.solver import SolverInput, find_conflicts
from app.solver.model import Assignment, EntryRef, RoomRef, SlotRef, TeacherRef
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

MATHS_PERIODS = 5
PE_PERIODS = 2
TOTAL_SESSIONS = MATHS_PERIODS + PE_PERIODS


def build_school(session: Session, days: int = 5, periods: int = 4) -> dict[str, int]:
    """One group studying maths with its tutor and PE with a specialist."""
    slots = [
        TimeSlot(
            day_of_week=day,
            period_index=period,
            start_time=time(9 + period, 0),
            end_time=time(9 + period, 45),
            is_break=False,
        )
        for day in range(days)
        for period in range(periods)
    ]
    session.add_all(slots)

    classroom = Room(name="Room 3A", room_type=RoomType.CLASSROOM, capacity=25)
    gym = Room(name="Gym", room_type=RoomType.GYM, capacity=60)
    session.add_all([classroom, gym])

    maths = Subject(code="MAT", name="Mathematics")
    physical_education = Subject(
        code="PE", name="Physical Education", required_room_type=RoomType.GYM
    )
    session.add_all([maths, physical_education])

    tutor = Teacher(
        first_name="Ana",
        last_name="Garcia",
        email="ana.garcia@example.org",
        max_periods_per_week=25,
    )
    specialist = Teacher(
        first_name="Luis",
        last_name="Moreno",
        email="luis.moreno@example.org",
        is_specialist=True,
        max_periods_per_week=25,
    )
    session.add_all([tutor, specialist])
    session.flush()

    group = ClassGroup(name="3A", grade=3, tutor_id=tutor.id, home_room_id=classroom.id)
    session.add(group)
    session.flush()

    maths_entry = CurriculumEntry(
        class_group_id=group.id,
        subject_id=maths.id,
        teacher_id=tutor.id,
        periods_per_week=MATHS_PERIODS,
    )
    pe_entry = CurriculumEntry(
        class_group_id=group.id,
        subject_id=physical_education.id,
        teacher_id=specialist.id,
        periods_per_week=PE_PERIODS,
    )
    session.add_all([maths_entry, pe_entry])
    session.commit()

    return {
        "group": group.id,
        "classroom": classroom.id,
        "gym": gym.id,
        "tutor": tutor.id,
        "specialist": specialist.id,
        "maths_entry": maths_entry.id,
        "pe_entry": pe_entry.id,
        "first_slot": slots[0].id,
    }


@pytest.fixture
def school(session: Session) -> dict[str, int]:
    return build_school(session)


def create_draft(client: TestClient, name: str = "Course 2026-2027") -> int:
    response = client.post("/api/v1/schedules", json={"name": name})
    assert response.status_code == 201
    schedule_id: int = response.json()["id"]
    return schedule_id


def solver_input_from(session: Session) -> SolverInput:
    """The same school as the service sees it, rebuilt independently."""
    slots = session.query(TimeSlot).all()
    rooms = session.query(Room).all()
    teachers = session.query(Teacher).all()
    entries = session.query(CurriculumEntry).all()
    unavailabilities = session.query(TeacherUnavailability).all()
    return SolverInput(
        slots=tuple(
            SlotRef(
                id=slot.id,
                day_of_week=slot.day_of_week,
                period_index=slot.period_index,
                is_break=slot.is_break,
            )
            for slot in slots
        ),
        rooms=tuple(RoomRef(id=room.id, room_type=str(room.room_type)) for room in rooms),
        teachers=tuple(
            TeacherRef(id=teacher.id, max_periods_per_week=teacher.max_periods_per_week)
            for teacher in teachers
        ),
        entries=tuple(
            EntryRef(
                id=entry.id,
                class_group_id=entry.class_group_id,
                subject_id=entry.subject_id,
                teacher_id=entry.teacher_id,
                periods_per_week=entry.periods_per_week,
                required_room_type=(
                    str(entry.subject.required_room_type)
                    if entry.subject.required_room_type is not None
                    else None
                ),
                home_room_id=entry.class_group.home_room_id,
            )
            for entry in entries
        ),
        unavailability=frozenset((row.teacher_id, row.time_slot_id) for row in unavailabilities),
    )


def stored_assignments(session: Session, schedule_id: int) -> Sequence[Assignment]:
    rows = session.query(ScheduledSession).filter(ScheduledSession.schedule_id == schedule_id).all()
    return [
        Assignment(entry_id=row.curriculum_entry_id, slot_id=row.time_slot_id, room_id=row.room_id)
        for row in rows
    ]


# -- generation ------------------------------------------------------------------


def test_generates_a_valid_timetable_from_orm_data(
    client: TestClient, session: Session, school: dict[str, int]
) -> None:
    schedule_id = create_draft(client)

    response = client.post(f"/api/v1/schedules/{schedule_id}/generate")

    assert response.status_code == 200
    summary = response.json()
    assert summary["solved"] is True
    assert summary["solver_status"] in ("optimal", "feasible")
    assert summary["sessions_placed"] == TOTAL_SESSIONS
    assert summary["generated_at"] is not None

    session.expire_all()
    assert (
        find_conflicts(solver_input_from(session), stored_assignments(session, schedule_id)) == []
    )
    assert client.get(f"/api/v1/schedules/{schedule_id}/conflicts").json() == {
        "schedule_id": schedule_id,
        "has_conflicts": False,
        "conflicts": [],
    }


def test_detail_expands_every_session_for_the_grid(
    client: TestClient, school: dict[str, int]
) -> None:
    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/generate")

    detail = client.get(f"/api/v1/schedules/{schedule_id}").json()

    assert detail["solver_status"] in ("optimal", "feasible")
    assert len(detail["sessions"]) == TOTAL_SESSIONS
    first = detail["sessions"][0]
    assert first["class_group_name"] == "3A"
    assert first["subject_code"] in ("MAT", "PE")
    assert first["teacher_name"] in ("Ana Garcia", "Luis Moreno")
    assert 0 <= first["day_of_week"] <= 4
    assert first["start_time"] is not None

    pe_sessions = [row for row in detail["sessions"] if row["subject_code"] == "PE"]
    assert len(pe_sessions) == PE_PERIODS
    assert all(row["room_name"] == "Gym" for row in pe_sessions)


def test_infeasible_input_is_reported_without_persisting_sessions(
    client: TestClient, session: Session
) -> None:
    """Seven weekly periods cannot fit in a two-period week."""
    build_school(session, days=1, periods=2)
    schedule_id = create_draft(client)

    response = client.post(f"/api/v1/schedules/{schedule_id}/generate")

    assert response.status_code == 200
    summary = response.json()
    assert summary["solved"] is False
    assert summary["solver_status"] == "infeasible"
    assert summary["sessions_placed"] == 0
    assert summary["message"]

    assert client.get(f"/api/v1/schedules/{schedule_id}").json()["sessions"] == []
    session.expire_all()
    assert session.query(ScheduledSession).count() == 0
    assert session.get(Schedule, schedule_id) is not None


def test_respects_teacher_unavailability_read_from_the_database(
    client: TestClient, session: Session, school: dict[str, int]
) -> None:
    monday = session.query(TimeSlot).filter(TimeSlot.day_of_week == 0).all()
    for slot in monday:
        session.add(TeacherUnavailability(teacher_id=school["tutor"], time_slot_id=slot.id))
    session.commit()

    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/generate")

    detail = client.get(f"/api/v1/schedules/{schedule_id}").json()
    maths_on_monday = [
        row
        for row in detail["sessions"]
        if row["subject_code"] == "MAT" and row["day_of_week"] == 0
    ]
    assert maths_on_monday == []


# -- locked sessions -------------------------------------------------------------


def test_locked_sessions_survive_a_regeneration(client: TestClient, school: dict[str, int]) -> None:
    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/generate")

    sessions = client.get(f"/api/v1/schedules/{schedule_id}").json()["sessions"]
    pinned = next(row for row in sessions if row["subject_code"] == "PE")
    locked = client.patch(
        f"/api/v1/schedules/{schedule_id}/sessions/{pinned['id']}", json={"locked": True}
    )
    assert locked.status_code == 200
    assert locked.json()["locked"] is True

    regenerated = client.post(f"/api/v1/schedules/{schedule_id}/generate")
    assert regenerated.json()["sessions_placed"] == TOTAL_SESSIONS

    after = client.get(f"/api/v1/schedules/{schedule_id}").json()["sessions"]
    survivor = next((row for row in after if row["id"] == pinned["id"]), None)
    assert survivor is not None, "the locked session kept its identity"
    assert survivor["locked"] is True
    assert survivor["time_slot_id"] == pinned["time_slot_id"]
    assert survivor["room_id"] == pinned["room_id"]
    assert len(after) == TOTAL_SESSIONS


# -- manual edits ----------------------------------------------------------------


def test_accepts_a_move_to_a_free_slot(
    client: TestClient, session: Session, school: dict[str, int]
) -> None:
    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/generate")
    sessions = client.get(f"/api/v1/schedules/{schedule_id}").json()["sessions"]

    used = {row["time_slot_id"] for row in sessions}
    free_slot = next(slot for slot in session.query(TimeSlot).all() if slot.id not in used)
    moved = client.patch(
        f"/api/v1/schedules/{schedule_id}/sessions/{sessions[0]['id']}",
        json={"time_slot_id": free_slot.id},
    )

    assert moved.status_code == 200
    assert moved.json()["time_slot_id"] == free_slot.id
    assert moved.json()["day_of_week"] == free_slot.day_of_week


def test_rejects_a_move_that_makes_the_group_overlap(
    client: TestClient, school: dict[str, int]
) -> None:
    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/generate")
    sessions = client.get(f"/api/v1/schedules/{schedule_id}").json()["sessions"]
    # PE and maths have different teachers and different rooms, so putting one on
    # top of the other breaks exactly one hard constraint: the group is in two
    # places at once.
    pe_session = next(row for row in sessions if row["subject_code"] == "PE")
    maths_session = next(row for row in sessions if row["subject_code"] == "MAT")

    response = client.patch(
        f"/api/v1/schedules/{schedule_id}/sessions/{pe_session['id']}",
        json={"time_slot_id": maths_session["time_slot_id"]},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
    assert "group_overlap" in response.json()["detail"]

    unchanged = client.get(f"/api/v1/schedules/{schedule_id}").json()["sessions"]
    assert {row["id"]: row["time_slot_id"] for row in unchanged} == {
        row["id"]: row["time_slot_id"] for row in sessions
    }


def test_rejects_a_move_into_a_slot_the_teacher_is_unavailable_in(
    client: TestClient, session: Session, school: dict[str, int]
) -> None:
    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/generate")
    sessions = client.get(f"/api/v1/schedules/{schedule_id}").json()["sessions"]
    maths = next(row for row in sessions if row["subject_code"] == "MAT")

    used = {row["time_slot_id"] for row in sessions}
    free_slot = next(slot for slot in session.query(TimeSlot).all() if slot.id not in used)
    session.add(TeacherUnavailability(teacher_id=school["tutor"], time_slot_id=free_slot.id))
    session.commit()

    response = client.patch(
        f"/api/v1/schedules/{schedule_id}/sessions/{maths['id']}",
        json={"time_slot_id": free_slot.id},
    )

    assert response.status_code == 409
    assert "teacher_unavailable" in response.json()["detail"]


def test_rejects_a_move_to_a_room_of_the_wrong_type(
    client: TestClient, school: dict[str, int]
) -> None:
    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/generate")
    sessions = client.get(f"/api/v1/schedules/{schedule_id}").json()["sessions"]
    pe_session = next(row for row in sessions if row["subject_code"] == "PE")

    response = client.patch(
        f"/api/v1/schedules/{schedule_id}/sessions/{pe_session['id']}",
        json={"room_id": school["classroom"]},
    )

    assert response.status_code == 409
    assert "wrong_room_type" in response.json()["detail"]


def test_returns_404_for_a_session_of_another_schedule(
    client: TestClient, school: dict[str, int]
) -> None:
    first = create_draft(client, "First")
    client.post(f"/api/v1/schedules/{first}/generate")
    session_id = client.get(f"/api/v1/schedules/{first}").json()["sessions"][0]["id"]
    other = create_draft(client, "Second")

    response = client.patch(
        f"/api/v1/schedules/{other}/sessions/{session_id}", json={"locked": True}
    )

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


# -- publishing ------------------------------------------------------------------


def test_only_one_schedule_is_published_at_a_time(
    client: TestClient, session: Session, school: dict[str, int]
) -> None:
    first = create_draft(client, "September")
    second = create_draft(client, "October")

    assert client.post(f"/api/v1/schedules/{first}/publish").json()["status"] == "published"
    published_second = client.post(f"/api/v1/schedules/{second}/publish")

    assert published_second.status_code == 200
    assert published_second.json()["status"] == "published"

    session.expire_all()
    statuses = {row.id: row.status for row in session.query(Schedule).all()}
    assert statuses[first] == ScheduleStatus.ARCHIVED
    assert statuses[second] == ScheduleStatus.PUBLISHED
    assert session.query(Schedule).filter(Schedule.status == ScheduleStatus.PUBLISHED).count() == 1


def test_a_published_schedule_cannot_be_generated_or_edited(
    client: TestClient, school: dict[str, int]
) -> None:
    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/generate")
    sessions = client.get(f"/api/v1/schedules/{schedule_id}").json()["sessions"]
    client.post(f"/api/v1/schedules/{schedule_id}/publish")

    regenerate = client.post(f"/api/v1/schedules/{schedule_id}/generate")
    assert regenerate.status_code == 409
    assert regenerate.json()["code"] == "conflict"

    edit = client.patch(
        f"/api/v1/schedules/{schedule_id}/sessions/{sessions[0]['id']}", json={"locked": True}
    )
    assert edit.status_code == 409


def test_republishing_the_same_schedule_is_a_conflict(
    client: TestClient, school: dict[str, int]
) -> None:
    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/publish")

    response = client.post(f"/api/v1/schedules/{schedule_id}/publish")

    assert response.status_code == 409


# -- listing and deletion --------------------------------------------------------


def test_lists_and_deletes_schedules(client: TestClient, school: dict[str, int]) -> None:
    schedule_id = create_draft(client)
    client.post(f"/api/v1/schedules/{schedule_id}/generate")

    listed = client.get("/api/v1/schedules").json()
    assert [row["id"] for row in listed] == [schedule_id]
    assert listed[0]["status"] == "draft"

    assert client.delete(f"/api/v1/schedules/{schedule_id}").status_code == 204
    assert client.get("/api/v1/schedules").json() == []
    assert client.get(f"/api/v1/schedules/{schedule_id}").status_code == 404


def test_returns_404_for_an_unknown_schedule(client: TestClient) -> None:
    assert client.get("/api/v1/schedules/999").status_code == 404
    assert client.post("/api/v1/schedules/999/generate").status_code == 404
