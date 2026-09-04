"""Persistence for :class:`~app.models.curriculum.CurriculumEntry`.

Besides queries on ``curriculum_entries`` itself, this repository resolves the
related rows (class group, subject, time slots, scheduled sessions) that the
service needs to validate and to build the workload report -- there is no
dedicated repository for those aggregates yet.
"""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.curriculum import CurriculumEntry
from app.models.schedule import ScheduledSession
from app.models.school import ClassGroup, Subject, TimeSlot
from app.repositories.base import BaseRepository


class CurriculumEntryRepository(BaseRepository[CurriculumEntry]):
    model = CurriculumEntry

    _DETAIL_OPTIONS = (
        selectinload(CurriculumEntry.class_group),
        selectinload(CurriculumEntry.subject),
        selectinload(CurriculumEntry.teacher),
    )

    def get_with_details(self, entry_id: int) -> CurriculumEntry | None:
        stmt = (
            select(CurriculumEntry)
            .where(CurriculumEntry.id == entry_id)
            .options(*self._DETAIL_OPTIONS)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_with_details(self) -> Sequence[CurriculumEntry]:
        stmt = select(CurriculumEntry).options(*self._DETAIL_OPTIONS)
        return self.session.execute(stmt).scalars().all()

    def get_by_group_and_subject(
        self, class_group_id: int, subject_id: int
    ) -> CurriculumEntry | None:
        stmt = select(CurriculumEntry).where(
            CurriculumEntry.class_group_id == class_group_id,
            CurriculumEntry.subject_id == subject_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_class_group(self, class_group_id: int) -> ClassGroup | None:
        return self.session.get(ClassGroup, class_group_id)

    def get_subject(self, subject_id: int) -> Subject | None:
        return self.session.get(Subject, subject_id)

    def list_all_class_groups(self) -> Sequence[ClassGroup]:
        return self.session.execute(select(ClassGroup)).scalars().all()

    def count_non_break_time_slots(self) -> int:
        stmt = select(func.count()).select_from(TimeSlot).where(~TimeSlot.is_break)
        return self.session.execute(stmt).scalar_one()

    def sum_periods_for_group(
        self, class_group_id: int, exclude_entry_id: int | None = None
    ) -> int:
        stmt = select(func.coalesce(func.sum(CurriculumEntry.periods_per_week), 0)).where(
            CurriculumEntry.class_group_id == class_group_id
        )
        if exclude_entry_id is not None:
            stmt = stmt.where(CurriculumEntry.id != exclude_entry_id)
        return self.session.execute(stmt).scalar_one()

    def sum_periods_for_teacher(self, teacher_id: int, exclude_entry_id: int | None = None) -> int:
        stmt = select(func.coalesce(func.sum(CurriculumEntry.periods_per_week), 0)).where(
            CurriculumEntry.teacher_id == teacher_id
        )
        if exclude_entry_id is not None:
            stmt = stmt.where(CurriculumEntry.id != exclude_entry_id)
        return self.session.execute(stmt).scalar_one()

    def periods_by_class_group(self) -> dict[int, int]:
        stmt = select(
            CurriculumEntry.class_group_id, func.sum(CurriculumEntry.periods_per_week)
        ).group_by(CurriculumEntry.class_group_id)
        return dict(self.session.execute(stmt).tuples().all())

    def periods_by_teacher(self) -> dict[int, int]:
        stmt = select(
            CurriculumEntry.teacher_id, func.sum(CurriculumEntry.periods_per_week)
        ).group_by(CurriculumEntry.teacher_id)
        return dict(self.session.execute(stmt).tuples().all())

    def has_scheduled_sessions(self, entry_id: int) -> bool:
        stmt = (
            select(func.count())
            .select_from(ScheduledSession)
            .where(ScheduledSession.curriculum_entry_id == entry_id)
        )
        return self.session.execute(stmt).scalar_one() > 0
