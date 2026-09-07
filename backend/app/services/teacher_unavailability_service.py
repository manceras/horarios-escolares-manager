"""Business rules for teacher unavailability."""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.school import TeacherUnavailability
from app.repositories.teacher_repository import TeacherRepository
from app.repositories.teacher_unavailability_repository import TeacherUnavailabilityRepository
from app.repositories.time_slot_repository import TimeSlotRepository
from app.schemas.teacher_unavailability import TeacherUnavailabilityCreate


class TeacherUnavailabilityService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.unavailabilities = TeacherUnavailabilityRepository(session)
        self.teachers = TeacherRepository(session)
        self.time_slots = TimeSlotRepository(session)

    def list_all(self, teacher_id: int | None = None) -> Sequence[TeacherUnavailability]:
        if teacher_id is not None:
            return self.unavailabilities.list_for_teacher(teacher_id)
        return self.unavailabilities.list_all()

    def get(self, unavailability_id: int) -> TeacherUnavailability:
        row = self.unavailabilities.get(unavailability_id)
        if row is None:
            raise NotFoundError(f"TeacherUnavailability {unavailability_id} not found")
        return row

    def create(self, payload: TeacherUnavailabilityCreate) -> TeacherUnavailability:
        if self.teachers.get(payload.teacher_id) is None:
            raise NotFoundError(f"Teacher {payload.teacher_id} not found")
        if self.time_slots.get(payload.time_slot_id) is None:
            raise NotFoundError(f"TimeSlot {payload.time_slot_id} not found")
        if (
            self.unavailabilities.get_by_teacher_and_slot(payload.teacher_id, payload.time_slot_id)
            is not None
        ):
            raise ConflictError(
                f"Teacher {payload.teacher_id} is already marked unavailable for "
                f"time slot {payload.time_slot_id}"
            )

        row = TeacherUnavailability(**payload.model_dump())
        self.unavailabilities.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def delete(self, unavailability_id: int) -> None:
        row = self.get(unavailability_id)
        self.unavailabilities.delete(row)
        self.session.commit()

    def replace_for_teacher(
        self, teacher_id: int, time_slot_ids: list[int]
    ) -> Sequence[TeacherUnavailability]:
        """Replace the full set of blocked slots for one teacher in one transaction."""
        if self.teachers.get(teacher_id) is None:
            raise NotFoundError(f"Teacher {teacher_id} not found")

        unique_slot_ids = set(time_slot_ids)
        for time_slot_id in unique_slot_ids:
            if self.time_slots.get(time_slot_id) is None:
                raise NotFoundError(f"TimeSlot {time_slot_id} not found")

        for existing in self.unavailabilities.list_for_teacher(teacher_id):
            self.unavailabilities.delete(existing)
        for time_slot_id in unique_slot_ids:
            self.unavailabilities.add(
                TeacherUnavailability(teacher_id=teacher_id, time_slot_id=time_slot_id)
            )

        self.session.commit()
        return self.unavailabilities.list_for_teacher(teacher_id)
