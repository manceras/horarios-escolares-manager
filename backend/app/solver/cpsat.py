"""OR-Tools CP-SAT implementation of :class:`~app.solver.base.TimetableSolver`.

Model, in one sentence: one boolean per (curriculum entry, teaching slot, candidate
room) saying "this session happens here". Hard constraints forbid combinations;
soft constraints add a penalty to the objective.
"""

from collections import defaultdict
from collections.abc import Sequence

from ortools.sat.python import cp_model

from app.solver.model import (
    Assignment,
    EntryRef,
    RoomRef,
    SlotRef,
    SolverInput,
    SolverOptions,
    SolverResult,
    SolverStatus,
)

_STATUS_MAP = {
    cp_model.OPTIMAL: SolverStatus.OPTIMAL,
    cp_model.FEASIBLE: SolverStatus.FEASIBLE,
    cp_model.INFEASIBLE: SolverStatus.INFEASIBLE,
}


class CpSatTimetableSolver:
    """Generates a timetable with constraint programming."""

    def solve(self, data: SolverInput, options: SolverOptions) -> SolverResult:
        teaching_slots = [slot for slot in data.slots if not slot.is_break]
        if not teaching_slots:
            return SolverResult(
                status=SolverStatus.INFEASIBLE, message="There are no teaching slots defined"
            )

        model = cp_model.CpModel()
        # place[(entry_id, slot_id, room_id)] -> BoolVar
        place: dict[tuple[int, int, int], cp_model.IntVar] = {}
        # occupies[(entry_id, slot_id)] -> BoolVar, true when the session happens in that slot
        occupies: dict[tuple[int, int], cp_model.IntVar] = {}

        for entry in data.entries:
            candidates = _candidate_rooms(entry, data.rooms)
            if not candidates:
                return SolverResult(
                    status=SolverStatus.INFEASIBLE,
                    message=(
                        f"Curriculum entry {entry.id} has no room of type "
                        f"{entry.required_room_type}"
                    ),
                )
            for slot in teaching_slots:
                slot_vars = []
                for room in candidates:
                    var = model.new_bool_var(f"place_e{entry.id}_s{slot.id}_r{room.id}")
                    place[(entry.id, slot.id, room.id)] = var
                    slot_vars.append(var)

                busy = model.new_bool_var(f"occupies_e{entry.id}_s{slot.id}")
                occupies[(entry.id, slot.id)] = busy
                model.add(sum(slot_vars) == busy)

                if (entry.teacher_id, slot.id) in data.unavailability:
                    model.add(busy == 0)

            # Exactly the required weekly load, no more and no less.
            model.add(
                sum(occupies[(entry.id, slot.id)] for slot in teaching_slots)
                == entry.periods_per_week
            )

        _add_no_overlap_constraints(model, data, teaching_slots, occupies, place)
        _add_teacher_load_constraints(model, data, teaching_slots, occupies)
        _fix_pinned_sessions(model, data, place, occupies)
        penalties = _add_same_subject_same_day_penalties(model, data, teaching_slots, occupies)

        if penalties:
            model.minimize(options.same_subject_same_day_penalty * sum(penalties))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = options.time_limit_seconds
        solver.parameters.random_seed = options.random_seed
        status = solver.solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return SolverResult(
                status=_STATUS_MAP.get(status, SolverStatus.UNKNOWN),
                message="No timetable satisfies every hard constraint",
            )

        assignments = tuple(
            Assignment(entry_id=entry_id, slot_id=slot_id, room_id=room_id)
            for (entry_id, slot_id, room_id), var in place.items()
            if solver.value(var) == 1
        )
        return SolverResult(
            status=_STATUS_MAP.get(status, SolverStatus.UNKNOWN),
            assignments=assignments,
            objective_value=int(solver.objective_value) if penalties else 0,
            message="",
            diagnostics={"sessions": len(assignments), "conflicts_relaxed": len(penalties)},
        )


def _candidate_rooms(entry: EntryRef, rooms: Sequence[RoomRef]) -> list[RoomRef]:
    """Rooms an entry may use, most specific rule first."""
    if entry.required_room_type is not None:
        return [room for room in rooms if room.room_type == entry.required_room_type]
    if entry.home_room_id is not None:
        return [room for room in rooms if room.id == entry.home_room_id]
    return [room for room in rooms if room.room_type == "classroom"]


def _add_no_overlap_constraints(
    model: cp_model.CpModel,
    data: SolverInput,
    slots: Sequence[SlotRef],
    occupies: dict[tuple[int, int], cp_model.IntVar],
    place: dict[tuple[int, int, int], cp_model.IntVar],
) -> None:
    """A teacher, a group and a room can each be in one place at a time."""
    by_teacher: dict[int, list[EntryRef]] = defaultdict(list)
    by_group: dict[int, list[EntryRef]] = defaultdict(list)
    for entry in data.entries:
        by_teacher[entry.teacher_id].append(entry)
        by_group[entry.class_group_id].append(entry)

    for slot in slots:
        for entries in by_teacher.values():
            model.add(sum(occupies[(entry.id, slot.id)] for entry in entries) <= 1)
        for entries in by_group.values():
            model.add(sum(occupies[(entry.id, slot.id)] for entry in entries) <= 1)
        for room in data.rooms:
            in_room = [
                var
                for (_, slot_id, room_id), var in place.items()
                if slot_id == slot.id and room_id == room.id
            ]
            if in_room:
                model.add(sum(in_room) <= 1)


def _add_teacher_load_constraints(
    model: cp_model.CpModel,
    data: SolverInput,
    slots: Sequence[SlotRef],
    occupies: dict[tuple[int, int], cp_model.IntVar],
) -> None:
    for teacher in data.teachers:
        entries = [entry for entry in data.entries if entry.teacher_id == teacher.id]
        if not entries:
            continue
        model.add(
            sum(occupies[(entry.id, slot.id)] for entry in entries for slot in slots)
            <= teacher.max_periods_per_week
        )


def _fix_pinned_sessions(
    model: cp_model.CpModel,
    data: SolverInput,
    place: dict[tuple[int, int, int], cp_model.IntVar],
    occupies: dict[tuple[int, int], cp_model.IntVar],
) -> None:
    """Locked sessions edited by a human must survive a re-run."""
    for pinned in data.fixed:
        if pinned.room_id is not None:
            key = (pinned.entry_id, pinned.slot_id, pinned.room_id)
            if key in place:
                model.add(place[key] == 1)
        elif (pinned.entry_id, pinned.slot_id) in occupies:
            model.add(occupies[(pinned.entry_id, pinned.slot_id)] == 1)


def _add_same_subject_same_day_penalties(
    model: cp_model.CpModel,
    data: SolverInput,
    slots: Sequence[SlotRef],
    occupies: dict[tuple[int, int], cp_model.IntVar],
) -> list[cp_model.IntVar]:
    """Soft constraint: avoid two sessions of the same entry on the same day."""
    slots_by_day: dict[int, list[SlotRef]] = defaultdict(list)
    for slot in slots:
        slots_by_day[slot.day_of_week].append(slot)

    penalties: list[cp_model.IntVar] = []
    for entry in data.entries:
        for day, day_slots in slots_by_day.items():
            excess = model.new_int_var(0, len(day_slots), f"excess_e{entry.id}_d{day}")
            model.add(sum(occupies[(entry.id, slot.id)] for slot in day_slots) <= 1 + excess)
            penalties.append(excess)
    return penalties
