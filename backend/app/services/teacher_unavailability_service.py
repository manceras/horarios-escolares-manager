"""Business rules for teacher unavailability.

Staff (admin, head_of_studies) may manage any teacher's unavailability. A user
with the ``teacher`` role may only create and delete their own rows.
"""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.models.enums import UserRole
from app.models.school import TeacherUnavailability
from app.models.user import User
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

    def _ensure_can_edit(self, user: User, teacher_id: int) -> None:
        """Staff may edit anyone's unavailability; a teacher may only edit their own."""
        if user.role == UserRole.TEACHER and user.teacher_id != teacher_id:
            raise PermissionDeniedError("Teachers may only edit their own unavailability")

    def create(self, payload: TeacherUnavailabilityCreate, user: User) -> TeacherUnavailability:
        self._ensure_can_edit(user, payload.teacher_id)
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

    def delete(self, unavailability_id: int, user: User) -> None:
        row = self.get(unavailability_id)
        self._ensure_can_edit(user, row.teacher_id)
        self.unavailabilities.delete(row)
        self.session.commit()

    def replace_for_teacher(
        self, teacher_id: int, time_slot_ids: list[int], user: User
    ) -> Sequence[TeacherUnavailability]:
        """Replace the full set of blocked slots for one teacher in one transaction."""
        self._ensure_can_edit(user, teacher_id)
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
