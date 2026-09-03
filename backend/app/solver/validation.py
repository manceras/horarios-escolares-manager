"""Hard-constraint checking for an existing set of assignments.

Used by tests, and by the API when a human edits a generated timetable by hand.
The solver guarantees these; this module proves it and catches manual mistakes.
"""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from app.solver.model import Assignment, SolverInput


@dataclass(frozen=True, slots=True)
class Conflict:
    code: str
    message: str
    entry_ids: tuple[int, ...]
    slot_id: int | None = None


def find_conflicts(data: SolverInput, assignments: Iterable[Assignment]) -> list[Conflict]:
    """Return every hard-constraint violation in ``assignments``.

    An empty list means the timetable is valid.
    """
    assignments = list(assignments)
    entries = {entry.id: entry for entry in data.entries}
    slots = {slot.id: slot for slot in data.slots}
    rooms = {room.id: room for room in data.rooms}
    teachers = {teacher.id: teacher for teacher in data.teachers}

    conflicts: list[Conflict] = []

    by_teacher_slot: dict[tuple[int, int], list[int]] = defaultdict(list)
    by_group_slot: dict[tuple[int, int], list[int]] = defaultdict(list)
    by_room_slot: dict[tuple[int, int], list[int]] = defaultdict(list)
    placed_per_entry: dict[int, int] = defaultdict(int)
    load_per_teacher: dict[int, int] = defaultdict(int)

    for assignment in assignments:
        entry = entries.get(assignment.entry_id)
        slot = slots.get(assignment.slot_id)
        if entry is None or slot is None:
            conflicts.append(
                Conflict(
                    code="unknown_reference",
                    message=f"Assignment references unknown entry or slot: {assignment}",
                    entry_ids=(assignment.entry_id,),
                    slot_id=assignment.slot_id,
                )
            )
            continue

        placed_per_entry[entry.id] += 1
        load_per_teacher[entry.teacher_id] += 1
        by_teacher_slot[(entry.teacher_id, slot.id)].append(entry.id)
        by_group_slot[(entry.class_group_id, slot.id)].append(entry.id)
        if assignment.room_id is not None:
            by_room_slot[(assignment.room_id, slot.id)].append(entry.id)

        if slot.is_break:
            conflicts.append(
                Conflict(
                    code="teaching_in_break",
                    message=f"Entry {entry.id} is placed in break slot {slot.id}",
                    entry_ids=(entry.id,),
                    slot_id=slot.id,
                )
            )

        if (entry.teacher_id, slot.id) in data.unavailability:
            conflicts.append(
                Conflict(
                    code="teacher_unavailable",
                    message=f"Teacher {entry.teacher_id} is unavailable in slot {slot.id}",
                    entry_ids=(entry.id,),
                    slot_id=slot.id,
                )
            )

        if entry.required_room_type is not None:
            room = rooms.get(assignment.room_id) if assignment.room_id is not None else None
            if room is None or room.room_type != entry.required_room_type:
                conflicts.append(
                    Conflict(
                        code="wrong_room_type",
                        message=(
                            f"Entry {entry.id} needs a room of type {entry.required_room_type}"
                        ),
                        entry_ids=(entry.id,),
                        slot_id=slot.id,
                    )
                )

    conflicts.extend(_overlaps(by_teacher_slot, "teacher_overlap", "Teacher"))
    conflicts.extend(_overlaps(by_group_slot, "group_overlap", "Class group"))
    conflicts.extend(_overlaps(by_room_slot, "room_overlap", "Room"))

    for entry in data.entries:
        placed = placed_per_entry[entry.id]
        if placed != entry.periods_per_week:
            conflicts.append(
                Conflict(
                    code="curriculum_not_covered",
                    message=(
                        f"Entry {entry.id} has {placed} sessions, expected {entry.periods_per_week}"
                    ),
                    entry_ids=(entry.id,),
                )
            )

    for teacher in teachers.values():
        if load_per_teacher[teacher.id] > teacher.max_periods_per_week:
            conflicts.append(
                Conflict(
                    code="teacher_overloaded",
                    message=(
                        f"Teacher {teacher.id} has {load_per_teacher[teacher.id]} periods, "
                        f"max is {teacher.max_periods_per_week}"
                    ),
                    entry_ids=(),
                )
            )

    return conflicts


def _overlaps(grouped: dict[tuple[int, int], list[int]], code: str, subject: str) -> list[Conflict]:
    return [
        Conflict(
            code=code,
            message=f"{subject} {owner_id} has {len(entry_ids)} sessions in slot {slot_id}",
            entry_ids=tuple(entry_ids),
            slot_id=slot_id,
        )
        for (owner_id, slot_id), entry_ids in grouped.items()
        if len(entry_ids) > 1
    ]
