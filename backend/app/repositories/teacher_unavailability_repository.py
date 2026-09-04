"""Persistence for :class:`~app.models.school.TeacherUnavailability`."""

from collections.abc import Sequence

from sqlalchemy import select

from app.models.school import TeacherUnavailability
from app.repositories.base import BaseRepository


class TeacherUnavailabilityRepository(BaseRepository[TeacherUnavailability]):
    model = TeacherUnavailability

    def list_for_teacher(self, teacher_id: int) -> Sequence[TeacherUnavailability]:
        return (
            self.session.execute(
                select(TeacherUnavailability).where(TeacherUnavailability.teacher_id == teacher_id)
            )
            .scalars()
            .all()
        )

    def get_by_teacher_and_slot(
        self, teacher_id: int, time_slot_id: int
    ) -> TeacherUnavailability | None:
        return self.session.execute(
            select(TeacherUnavailability).where(
                TeacherUnavailability.teacher_id == teacher_id,
                TeacherUnavailability.time_slot_id == time_slot_id,
            )
        ).scalar_one_or_none()
