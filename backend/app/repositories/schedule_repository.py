"""Persistence for :class:`~app.models.schedule.Schedule` and its sessions.

It also reads the school data the solver needs (slots, rooms, teachers,
curriculum, unavailabilities). Those rows are never written here; they are the
inputs of a generation run, so loading them eagerly in one place keeps the
service free of queries and the run free of N+1 lookups.
"""

from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload, selectinload

from app.models.curriculum import CurriculumEntry
from app.models.enums import ScheduleStatus
from app.models.schedule import Schedule, ScheduledSession
from app.models.school import Room, Teacher, TeacherUnavailability, TimeSlot
from app.repositories.base import BaseRepository

_SESSION_LABELS = (
    joinedload(ScheduledSession.curriculum_entry).joinedload(CurriculumEntry.class_group),
    joinedload(ScheduledSession.curriculum_entry).joinedload(CurriculumEntry.subject),
    joinedload(ScheduledSession.curriculum_entry).joinedload(CurriculumEntry.teacher),
    joinedload(ScheduledSession.time_slot),
    joinedload(ScheduledSession.room),
)


class ScheduleRepository(BaseRepository[Schedule]):
    model = Schedule

    def list_all(self) -> Sequence[Schedule]:
        return self.session.execute(select(Schedule).order_by(Schedule.id.desc())).scalars().all()

    def get_published(self) -> Schedule | None:
        return self.session.execute(
            select(Schedule).where(Schedule.status == ScheduleStatus.PUBLISHED)
        ).scalar_one_or_none()

    # -- sessions of one schedule ------------------------------------------------

    def list_sessions(self, schedule_id: int) -> Sequence[ScheduledSession]:
        """Every session of a schedule with the labels the grid needs."""
        statement = (
            select(ScheduledSession)
            .where(ScheduledSession.schedule_id == schedule_id)
            .options(*_SESSION_LABELS)
        )
        return self.session.execute(statement).unique().scalars().all()

    def get_session(self, schedule_id: int, session_id: int) -> ScheduledSession | None:
        statement = (
            select(ScheduledSession)
            .where(
                ScheduledSession.id == session_id,
                ScheduledSession.schedule_id == schedule_id,
            )
            .options(*_SESSION_LABELS)
        )
        return self.session.execute(statement).unique().scalar_one_or_none()

    def delete_unlocked_sessions(self, schedule_id: int) -> None:
        self.session.execute(
            delete(ScheduledSession).where(
                ScheduledSession.schedule_id == schedule_id,
                ScheduledSession.locked.is_(False),
            )
        )
        self.session.flush()

    def add_session(self, scheduled_session: ScheduledSession) -> ScheduledSession:
        self.session.add(scheduled_session)
        return scheduled_session

    # -- solver inputs -----------------------------------------------------------

    def list_time_slots(self) -> Sequence[TimeSlot]:
        return (
            self.session.execute(
                select(TimeSlot).order_by(TimeSlot.day_of_week, TimeSlot.period_index)
            )
            .scalars()
            .all()
        )

    def get_time_slot(self, time_slot_id: int) -> TimeSlot | None:
        return self.session.get(TimeSlot, time_slot_id)

    def list_rooms(self) -> Sequence[Room]:
        return self.session.execute(select(Room).order_by(Room.id)).scalars().all()

    def get_room(self, room_id: int) -> Room | None:
        return self.session.get(Room, room_id)

    def list_teachers(self) -> Sequence[Teacher]:
        return self.session.execute(select(Teacher).order_by(Teacher.id)).scalars().all()

    def list_curriculum_entries(self) -> Sequence[CurriculumEntry]:
        """Curriculum entries with the subject and group the solver reads."""
        statement = (
            select(CurriculumEntry)
            .options(
                selectinload(CurriculumEntry.subject),
                selectinload(CurriculumEntry.class_group),
            )
            .order_by(CurriculumEntry.id)
        )
        return self.session.execute(statement).scalars().all()

    def list_unavailabilities(self) -> Sequence[TeacherUnavailability]:
        return self.session.execute(select(TeacherUnavailability)).scalars().all()
