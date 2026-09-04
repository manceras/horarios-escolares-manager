"""Persistence for :class:`~app.models.school.TimeSlot`."""

from sqlalchemy import select

from app.models.school import TimeSlot
from app.repositories.base import BaseRepository


class TimeSlotRepository(BaseRepository[TimeSlot]):
    model = TimeSlot

    def get_by_day_and_period(self, day_of_week: int, period_index: int) -> TimeSlot | None:
        return self.session.execute(
            select(TimeSlot).where(
                TimeSlot.day_of_week == day_of_week,
                TimeSlot.period_index == period_index,
            )
        ).scalar_one_or_none()
