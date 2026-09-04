"""Business rules for schedules.

This is the bridge between the ORM and the pure solver: it reads the school out
of the database into a :class:`~app.solver.model.SolverInput`, runs the solver,
and writes the resulting assignments back as ``ScheduledSession`` rows. The
solver itself never sees a session, a query or a transaction.
"""

from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import ConflictError, NotFoundError
from app.models.enums import ScheduleStatus
from app.models.schedule import Schedule, ScheduledSession
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import (
    ConflictRead,
    ConflictReport,
    GenerationResult,
    ScheduleCreate,
    ScheduleDetail,
    ScheduledSessionRead,
    ScheduledSessionUpdate,
    ScheduleRead,
)
from app.solver.base import TimetableSolver
from app.solver.cpsat import CpSatTimetableSolver
from app.solver.model import (
    Assignment,
    EntryRef,
    RoomRef,
    SlotRef,
    SolverInput,
    SolverOptions,
    TeacherRef,
)
from app.solver.validation import Conflict, find_conflicts

# A conflict reduced to a comparable identity, so two reports can be diffed.
type _ConflictKey = tuple[str, tuple[int, ...], int | None]


class ScheduleService:
    def __init__(self, session: Session, solver: TimetableSolver | None = None) -> None:
        self.session = session
        self.schedules = ScheduleRepository(session)
        # The protocol is the seam described in docs/adr/0003-cp-sat-solver.md.
        self.solver: TimetableSolver = solver or CpSatTimetableSolver()

    # -- reads -------------------------------------------------------------------

    def list_all(self) -> Sequence[Schedule]:
        return self.schedules.list_all()

    def get(self, schedule_id: int) -> Schedule:
        schedule = self.schedules.get(schedule_id)
        if schedule is None:
            raise NotFoundError(f"Schedule {schedule_id} not found")
        return schedule

    def get_detail(self, schedule_id: int) -> ScheduleDetail:
        """The schedule plus every session, expanded for the weekly grid."""
        schedule = self.get(schedule_id)
        sessions = self.schedules.list_sessions(schedule.id)
        return ScheduleDetail(
            **ScheduleRead.model_validate(schedule).model_dump(),
            sessions=[_to_session_read(session) for session in _in_grid_order(sessions)],
        )

    def find_conflicts(self, schedule_id: int) -> ConflictReport:
        """Re-check the stored timetable against every hard constraint."""
        schedule = self.get(schedule_id)
        data = self._build_solver_input()
        sessions = self.schedules.list_sessions(schedule.id)
        conflicts = find_conflicts(data, [_to_assignment(session) for session in sessions])
        return ConflictReport(
            schedule_id=schedule.id,
            has_conflicts=bool(conflicts),
            conflicts=[_to_conflict_read(conflict) for conflict in conflicts],
        )

    # -- writes ------------------------------------------------------------------

    def create(self, payload: ScheduleCreate) -> Schedule:
        schedule = Schedule(name=payload.name, status=ScheduleStatus.DRAFT)
        self.schedules.add(schedule)
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def delete(self, schedule_id: int) -> None:
        schedule = self.get(schedule_id)
        self.schedules.delete(schedule)
        self.session.commit()

    def publish(self, schedule_id: int) -> Schedule:
        """Make this schedule the published one, archiving the previous one.

        At most one schedule is published at a time (docs/domain-model.md).
        """
        schedule = self.get(schedule_id)
        if schedule.status == ScheduleStatus.PUBLISHED:
            raise ConflictError(f"Schedule {schedule.id} is already published")
        if schedule.status == ScheduleStatus.ARCHIVED:
            raise ConflictError(f"Schedule {schedule.id} is archived and cannot be published")

        current = self.schedules.get_published()
        if current is not None and current.id != schedule.id:
            current.status = ScheduleStatus.ARCHIVED

        schedule.status = ScheduleStatus.PUBLISHED
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def generate(self, schedule_id: int) -> GenerationResult:
        """Run the solver and persist the timetable it found.

        Locked sessions are fed back in as fixed assignments and survive the run.
        An infeasible run changes no session: the caller gets the status and the
        solver's message so it can tell the user the constraints are impossible.
        """
        schedule = self.get(schedule_id)
        self._ensure_editable(schedule)

        stored = self.schedules.list_sessions(schedule.id)
        locked = [session for session in stored if session.locked]
        data = self._build_solver_input(fixed=tuple(_to_assignment(session) for session in locked))
        options = SolverOptions(time_limit_seconds=get_settings().solver_time_limit_seconds)

        result = self.solver.solve(data, options)

        schedule.solver_status = str(result.status)
        if not result.solved:
            # Nothing is written: a partial timetable is worse than none at all.
            self.session.commit()
            self.session.refresh(schedule)
            return GenerationResult(
                schedule_id=schedule.id,
                solver_status=result.status,
                solved=False,
                sessions_placed=0,
                penalty=result.objective_value,
                message=result.message or "No timetable satisfies every hard constraint",
                generated_at=schedule.generated_at,
            )

        self._replace_sessions(schedule, locked, result.assignments)
        schedule.generated_at = _utc_now()
        self.session.commit()
        self.session.refresh(schedule)

        return GenerationResult(
            schedule_id=schedule.id,
            solver_status=result.status,
            solved=True,
            sessions_placed=len(result.assignments),
            penalty=result.objective_value,
            message=result.message,
            generated_at=schedule.generated_at,
        )

    def update_session(
        self, schedule_id: int, session_id: int, payload: ScheduledSessionUpdate
    ) -> ScheduledSessionRead:
        """Move a session, change its room or pin it, re-checking hard constraints.

        The edit is applied to a copy of the timetable and validated with
        ``find_conflicts``. Only violations the edit introduces reject it: a draft
        that is still incomplete already reports missing sessions, and that is not
        this edit's fault.
        """
        schedule = self.get(schedule_id)
        self._ensure_editable(schedule)

        target = self.schedules.get_session(schedule.id, session_id)
        if target is None:
            raise NotFoundError(f"Session {session_id} not found in schedule {schedule_id}")

        changes = payload.model_dump(exclude_unset=True)
        new_slot_id = changes.get("time_slot_id", target.time_slot_id)
        new_room_id = changes.get("room_id", target.room_id)
        if new_slot_id is None:
            raise ConflictError("A session must stay in a time slot")

        if new_slot_id != target.time_slot_id and self.schedules.get_time_slot(new_slot_id) is None:
            raise NotFoundError(f"Time slot {new_slot_id} not found")
        if (
            new_room_id is not None
            and new_room_id != target.room_id
            and self.schedules.get_room(new_room_id) is None
        ):
            raise NotFoundError(f"Room {new_room_id} not found")

        self._reject_if_it_breaks_a_constraint(schedule.id, target, new_slot_id, new_room_id)

        target.time_slot_id = new_slot_id
        target.room_id = new_room_id
        if "locked" in changes and changes["locked"] is not None:
            target.locked = changes["locked"]
        self.session.commit()

        moved = self.schedules.get_session(schedule.id, session_id)
        if moved is None:  # pragma: no cover - the row was just committed
            raise NotFoundError(f"Session {session_id} not found in schedule {schedule_id}")
        return _to_session_read(moved)

    # -- internals ---------------------------------------------------------------

    def _ensure_editable(self, schedule: Schedule) -> None:
        """A published schedule is what the school reads; it is archived, not edited."""
        # SQLite hands the column back as a plain string, so compare by value.
        if schedule.status != ScheduleStatus.DRAFT:
            raise ConflictError(
                f"Schedule {schedule.id} is {schedule.status} and can no longer be edited"
            )

    def _build_solver_input(self, fixed: tuple[Assignment, ...] = ()) -> SolverInput:
        """Read the whole school into the solver's plain dataclasses."""
        slots = tuple(
            SlotRef(
                id=slot.id,
                day_of_week=slot.day_of_week,
                period_index=slot.period_index,
                is_break=slot.is_break,
            )
            for slot in self.schedules.list_time_slots()
        )
        rooms = tuple(
            RoomRef(id=room.id, room_type=str(room.room_type))
            for room in self.schedules.list_rooms()
        )
        teachers = tuple(
            TeacherRef(id=teacher.id, max_periods_per_week=teacher.max_periods_per_week)
            for teacher in self.schedules.list_teachers()
        )
        entries = tuple(
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
            for entry in self.schedules.list_curriculum_entries()
        )
        unavailability = frozenset(
            (row.teacher_id, row.time_slot_id) for row in self.schedules.list_unavailabilities()
        )
        return SolverInput(
            slots=slots,
            rooms=rooms,
            teachers=teachers,
            entries=entries,
            unavailability=unavailability,
            fixed=fixed,
        )

    def _replace_sessions(
        self,
        schedule: Schedule,
        locked: Sequence[ScheduledSession],
        assignments: Sequence[Assignment],
    ) -> None:
        """Swap the generated part of the timetable for the solver's answer.

        Locked rows keep their identity, so a pin a human set survives with the
        same id. Everything else is deleted and rewritten.
        """
        self.schedules.delete_unlocked_sessions(schedule.id)
        pinned = {
            (session.curriculum_entry_id, session.time_slot_id): session for session in locked
        }

        for assignment in assignments:
            kept = pinned.get((assignment.entry_id, assignment.slot_id))
            if kept is not None:
                # The solver had to choose a room for a pin that had none.
                if kept.room_id is None:
                    kept.room_id = assignment.room_id
                continue
            self.schedules.add_session(
                ScheduledSession(
                    schedule_id=schedule.id,
                    curriculum_entry_id=assignment.entry_id,
                    time_slot_id=assignment.slot_id,
                    room_id=assignment.room_id,
                    locked=False,
                )
            )

    def _reject_if_it_breaks_a_constraint(
        self,
        schedule_id: int,
        target: ScheduledSession,
        new_slot_id: int,
        new_room_id: int | None,
    ) -> None:
        data = self._build_solver_input()
        stored = self.schedules.list_sessions(schedule_id)

        before = [_to_assignment(session) for session in stored]
        after = [
            Assignment(
                entry_id=target.curriculum_entry_id, slot_id=new_slot_id, room_id=new_room_id
            )
            if session.id == target.id
            else _to_assignment(session)
            for session in stored
        ]

        introduced = _new_conflicts(find_conflicts(data, before), find_conflicts(data, after))
        if introduced:
            first = introduced[0]
            raise ConflictError(
                f"The move breaks a hard constraint ({first.code}): {first.message}"
            )


def _utc_now() -> datetime:
    """Naive UTC, matching the ``DateTime`` columns SQLite stores."""
    return datetime.now(UTC).replace(tzinfo=None)


def _in_grid_order(sessions: Sequence[ScheduledSession]) -> list[ScheduledSession]:
    return sorted(
        sessions,
        key=lambda session: (
            session.time_slot.day_of_week,
            session.time_slot.period_index,
            session.curriculum_entry.class_group.name,
        ),
    )


def _to_assignment(session: ScheduledSession) -> Assignment:
    return Assignment(
        entry_id=session.curriculum_entry_id,
        slot_id=session.time_slot_id,
        room_id=session.room_id,
    )


def _to_session_read(session: ScheduledSession) -> ScheduledSessionRead:
    entry = session.curriculum_entry
    slot = session.time_slot
    return ScheduledSessionRead(
        id=session.id,
        curriculum_entry_id=entry.id,
        class_group_id=entry.class_group_id,
        class_group_name=entry.class_group.name,
        subject_id=entry.subject_id,
        subject_code=entry.subject.code,
        subject_name=entry.subject.name,
        teacher_id=entry.teacher_id,
        teacher_name=entry.teacher.full_name,
        room_id=session.room_id,
        room_name=session.room.name if session.room is not None else None,
        time_slot_id=slot.id,
        day_of_week=slot.day_of_week,
        period_index=slot.period_index,
        start_time=slot.start_time,
        end_time=slot.end_time,
        locked=session.locked,
    )


def _to_conflict_read(conflict: Conflict) -> ConflictRead:
    return ConflictRead(
        code=conflict.code,
        message=conflict.message,
        entry_ids=list(conflict.entry_ids),
        slot_id=conflict.slot_id,
    )


def _conflict_key(conflict: Conflict) -> _ConflictKey:
    return (conflict.code, tuple(sorted(conflict.entry_ids)), conflict.slot_id)


def _new_conflicts(before: Sequence[Conflict], after: Sequence[Conflict]) -> list[Conflict]:
    """Conflicts the edit introduced, ignoring the ones already there."""
    existing = Counter(_conflict_key(conflict) for conflict in before)
    introduced: list[Conflict] = []
    for conflict in after:
        key = _conflict_key(conflict)
        if existing[key] > 0:
            existing[key] -= 1
        else:
            introduced.append(conflict)
    return introduced
