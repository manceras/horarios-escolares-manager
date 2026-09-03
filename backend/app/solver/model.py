"""Data the solver works with.

Everything here is immutable and framework-free. The service layer is
responsible for building a :class:`SolverInput` from ORM entities and for
persisting the resulting :class:`Assignment` list.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class SolverStatus(StrEnum):
    OPTIMAL = "optimal"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SlotRef:
    id: int
    day_of_week: int
    period_index: int
    is_break: bool = False


@dataclass(frozen=True, slots=True)
class RoomRef:
    id: int
    room_type: str


@dataclass(frozen=True, slots=True)
class TeacherRef:
    id: int
    max_periods_per_week: int


@dataclass(frozen=True, slots=True)
class EntryRef:
    """One curriculum entry to place."""

    id: int
    class_group_id: int
    subject_id: int
    teacher_id: int
    periods_per_week: int
    # When set, the entry may only use rooms of this type (gym, music, ...).
    required_room_type: str | None = None
    # Room used when the subject has no special requirement (the group's classroom).
    home_room_id: int | None = None


@dataclass(frozen=True, slots=True)
class Assignment:
    entry_id: int
    slot_id: int
    room_id: int | None = None


@dataclass(frozen=True, slots=True)
class SolverInput:
    slots: tuple[SlotRef, ...]
    rooms: tuple[RoomRef, ...]
    teachers: tuple[TeacherRef, ...]
    entries: tuple[EntryRef, ...]
    # (teacher_id, slot_id) pairs in which the teacher cannot teach.
    unavailability: frozenset[tuple[int, int]] = frozenset()
    # Sessions pinned by a human; the solver must reproduce them exactly.
    fixed: tuple[Assignment, ...] = ()


@dataclass(frozen=True, slots=True)
class SolverOptions:
    time_limit_seconds: float = 30.0
    random_seed: int = 0
    # Penalty for placing the same subject twice in a day for the same group.
    same_subject_same_day_penalty: int = 10


@dataclass(frozen=True, slots=True)
class SolverResult:
    status: SolverStatus
    assignments: tuple[Assignment, ...] = ()
    objective_value: int | None = None
    message: str = ""
    diagnostics: dict[str, int] = field(default_factory=dict)

    @property
    def solved(self) -> bool:
        return self.status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
