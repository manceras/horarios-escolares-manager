"""Persistence for :class:`~app.models.schedule.ScheduledSession`.

Scheduled sessions are not exposed through their own CRUD slice yet; this
repository only supports the reference check ``TimeSlotService`` needs before
deleting a slot.
"""

from sqlalchemy import select

from app.models.schedule import ScheduledSession
from app.repositories.base import BaseRepository


class ScheduledSessionRepository(BaseRepository[ScheduledSession]):
    model = ScheduledSession

    def exists_for_time_slot(self, time_slot_id: int) -> bool:
        result = self.session.execute(
            select(ScheduledSession.id)
            .where(ScheduledSession.time_slot_id == time_slot_id)
            .limit(1)
        ).first()
        return result is not None
