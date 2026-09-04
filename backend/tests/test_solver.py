"""Solver behaviour. Every hard constraint from docs/domain-model.md is covered."""

import pytest
from app.solver import (
    Assignment,
    CpSatTimetableSolver,
    EntryRef,
    RoomRef,
    SlotRef,
    SolverInput,
    SolverOptions,
    SolverStatus,
    TeacherRef,
    find_conflicts,
)

OPTIONS = SolverOptions(time_limit_seconds=10.0)


def slots(days: int = 5, periods: int = 4) -> tuple[SlotRef, ...]:
    return tuple(
        SlotRef(id=day * periods + period, day_of_week=day, period_index=period)
        for day in range(days)
        for period in range(periods)
    )


def small_school(**overrides: object) -> SolverInput:
    """One group, one tutor, one PE specialist, a classroom and a gym."""
    data = {
        "slots": slots(),
        "rooms": (RoomRef(id=1, room_type="classroom"), RoomRef(id=2, room_type="gym")),
        "teachers": (
            TeacherRef(id=1, max_periods_per_week=25),
            TeacherRef(id=2, max_periods_per_week=25),
        ),
        "entries": (
            EntryRef(
                id=10,
                class_group_id=100,
                subject_id=1,
                teacher_id=1,
                periods_per_week=5,
                home_room_id=1,
            ),
            EntryRef(
                id=11,
                class_group_id=100,
                subject_id=2,
                teacher_id=2,
                periods_per_week=2,
                required_room_type="gym",
            ),
        ),
    }
    data.update(overrides)
    return SolverInput(**data)  # type: ignore[arg-type]


def test_produces_a_conflict_free_timetable() -> None:
    data = small_school()

    result = CpSatTimetableSolver().solve(data, OPTIONS)

    assert result.status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
    assert len(result.assignments) == 7
    assert find_conflicts(data, result.assignments) == []


def test_respects_teacher_unavailability() -> None:
    blocked = frozenset((1, slot.id) for slot in slots() if slot.day_of_week == 0)
    data = small_school(unavailability=blocked)

    result = CpSatTimetableSolver().solve(data, OPTIONS)

    assert result.solved
    monday_slot_ids = {slot.id for slot in data.slots if slot.day_of_week == 0}
    teacher_one_entries = {entry.id for entry in data.entries if entry.teacher_id == 1}
    assert not any(
        assignment.slot_id in monday_slot_ids and assignment.entry_id in teacher_one_entries
        for assignment in result.assignments
    )


def test_never_places_a_session_in_a_break() -> None:
    day_slots = (
        SlotRef(id=1, day_of_week=0, period_index=0),
        SlotRef(id=2, day_of_week=0, period_index=1, is_break=True),
        SlotRef(id=3, day_of_week=1, period_index=0),
    )
    data = SolverInput(
        slots=day_slots,
        rooms=(RoomRef(id=1, room_type="classroom"),),
        teachers=(TeacherRef(id=1, max_periods_per_week=25),),
        entries=(
            EntryRef(
                id=10,
                class_group_id=100,
                subject_id=1,
                teacher_id=1,
                periods_per_week=2,
                home_room_id=1,
            ),
        ),
    )

    result = CpSatTimetableSolver().solve(data, OPTIONS)

    assert result.solved
    assert {assignment.slot_id for assignment in result.assignments} == {1, 3}


def test_uses_a_room_of_the_required_type() -> None:
    data = small_school()

    result = CpSatTimetableSolver().solve(data, OPTIONS)

    gym_sessions = [a for a in result.assignments if a.entry_id == 11]
    assert len(gym_sessions) == 2
    assert all(assignment.room_id == 2 for assignment in gym_sessions)


def test_reports_infeasible_when_there_are_not_enough_slots() -> None:
    data = small_school(slots=slots(days=1, periods=2))

    result = CpSatTimetableSolver().solve(data, OPTIONS)

    assert result.status is SolverStatus.INFEASIBLE
    assert not result.assignments


def test_keeps_locked_sessions() -> None:
    pinned = Assignment(entry_id=11, slot_id=0, room_id=2)
    data = small_school(fixed=(pinned,))

    result = CpSatTimetableSolver().solve(data, OPTIONS)

    assert result.solved
    assert pinned in result.assignments


def test_two_teachers_may_not_share_a_room_at_the_same_time() -> None:
    """Both groups need the gym twice a week; the gym holds one session per slot."""
    data = SolverInput(
        slots=slots(days=1, periods=4),
        rooms=(RoomRef(id=2, room_type="gym"),),
        teachers=(
            TeacherRef(id=1, max_periods_per_week=25),
            TeacherRef(id=2, max_periods_per_week=25),
        ),
        entries=(
            EntryRef(
                id=10,
                class_group_id=100,
                subject_id=1,
                teacher_id=1,
                periods_per_week=2,
                required_room_type="gym",
            ),
            EntryRef(
                id=11,
                class_group_id=200,
                subject_id=1,
                teacher_id=2,
                periods_per_week=2,
                required_room_type="gym",
            ),
        ),
    )

    result = CpSatTimetableSolver().solve(data, OPTIONS)

    assert result.solved
    assert find_conflicts(data, result.assignments) == []
    assert len({assignment.slot_id for assignment in result.assignments}) == 4


@pytest.mark.parametrize(
    ("bad_assignments", "expected_code"),
    [
        ([Assignment(entry_id=10, slot_id=0, room_id=1)], "curriculum_not_covered"),
        (
            [Assignment(entry_id=11, slot_id=0, room_id=1)],
            "wrong_room_type",
        ),
    ],
)
def test_find_conflicts_detects_invalid_timetables(
    bad_assignments: list[Assignment], expected_code: str
) -> None:
    conflicts = find_conflicts(small_school(), bad_assignments)

    assert expected_code in {conflict.code for conflict in conflicts}


def test_reports_infeasible_when_a_locked_session_can_no_longer_be_placed() -> None:
    """A pin the model cannot express must fail loudly, not be dropped silently.

    This happens when school data changes under an existing lock: the slot is
    turned into a break, or the room stops matching the subject. Ignoring the pin
    would return an "optimal" timetable that contradicts what a human pinned.
    """
    day_slots = (
        SlotRef(id=1, day_of_week=0, period_index=0),
        SlotRef(id=2, day_of_week=0, period_index=1, is_break=True),
        SlotRef(id=3, day_of_week=1, period_index=0),
    )
    data = SolverInput(
        slots=day_slots,
        rooms=(RoomRef(id=1, room_type="classroom"),),
        teachers=(TeacherRef(id=1, max_periods_per_week=25),),
        entries=(
            EntryRef(
                id=10,
                class_group_id=100,
                subject_id=1,
                teacher_id=1,
                periods_per_week=1,
                home_room_id=1,
            ),
        ),
        # Slot 2 became a break after the session was locked into it.
        fixed=(Assignment(entry_id=10, slot_id=2, room_id=1),),
    )

    result = CpSatTimetableSolver().solve(data, OPTIONS)

    assert result.status is SolverStatus.INFEASIBLE
    assert not result.assignments
    assert "10" in result.message


def test_the_same_input_always_produces_the_same_timetable() -> None:
    data = small_school()
    solver = CpSatTimetableSolver()

    first = solver.solve(data, OPTIONS)
    second = solver.solve(data, OPTIONS)

    assert set(first.assignments) == set(second.assignments)
