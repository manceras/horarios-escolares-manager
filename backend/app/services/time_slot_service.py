"""Business rules for time slots."""

from collections.abc import Sequence
from datetime import time

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.models.school import TimeSlot
from app.repositories.scheduled_session_repository import ScheduledSessionRepository
from app.repositories.time_slot_repository import TimeSlotRepository
from app.schemas.time_slot import TimeSlotCreate, TimeSlotUpdate


class TimeSlotService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.time_slots = TimeSlotRepository(session)
        self.scheduled_sessions = ScheduledSessionRepository(session)

    def list_all(self) -> Sequence[TimeSlot]:
        return self.time_slots.list_all()

    def get(self, time_slot_id: int) -> TimeSlot:
        time_slot = self.time_slots.get(time_slot_id)
        if time_slot is None:
            raise NotFoundError(f"TimeSlot {time_slot_id} not found")
        return time_slot

    def _validate(self, day_of_week: int, start_time: time, end_time: time) -> None:
        if not 0 <= day_of_week <= 4:
            raise ValidationError("day_of_week must be between 0 (Monday) and 4 (Friday)")
        if start_time >= end_time:
            raise ValidationError("start_time must be strictly before end_time")

    def create(self, payload: TimeSlotCreate) -> TimeSlot:
        self._validate(payload.day_of_week, payload.start_time, payload.end_time)
        existing = self.time_slots.get_by_day_and_period(payload.day_of_week, payload.period_index)
        if existing is not None:
            raise ConflictError(
                f"A time slot already exists for day {payload.day_of_week}, "
                f"period {payload.period_index}"
            )

        time_slot = TimeSlot(**payload.model_dump())
        self.time_slots.add(time_slot)
        self.session.commit()
        self.session.refresh(time_slot)
        return time_slot

    def update(self, time_slot_id: int, payload: TimeSlotUpdate) -> TimeSlot:
        time_slot = self.get(time_slot_id)
        changes = payload.model_dump(exclude_unset=True)

        new_day = changes.get("day_of_week", time_slot.day_of_week)
        new_period = changes.get("period_index", time_slot.period_index)
        new_start = changes.get("start_time", time_slot.start_time)
        new_end = changes.get("end_time", time_slot.end_time)
        self._validate(new_day, new_start, new_end)

        if (new_day, new_period) != (time_slot.day_of_week, time_slot.period_index):
            existing = self.time_slots.get_by_day_and_period(new_day, new_period)
            if existing is not None:
                raise ConflictError(
                    f"A time slot already exists for day {new_day}, period {new_period}"
                )

        for field, value in changes.items():
            setattr(time_slot, field, value)
        self.session.commit()
        self.session.refresh(time_slot)
        return time_slot

    def delete(self, time_slot_id: int) -> None:
        time_slot = self.get(time_slot_id)
        if self.scheduled_sessions.exists_for_time_slot(time_slot_id):
            raise ConflictError(f"TimeSlot {time_slot_id} is referenced by a scheduled session")
        self.time_slots.delete(time_slot)
        self.session.commit()
