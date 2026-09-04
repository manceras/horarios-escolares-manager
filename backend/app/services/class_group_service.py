"""Business rules for class groups."""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.school import ClassGroup
from app.repositories.class_group_repository import ClassGroupRepository
from app.repositories.curriculum_entry_repository import CurriculumEntryRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.teacher_repository import TeacherRepository
from app.schemas.class_group import ClassGroupCreate, ClassGroupUpdate


class ClassGroupService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.class_groups = ClassGroupRepository(session)
        self.teachers = TeacherRepository(session)
        self.rooms = RoomRepository(session)
        self.curriculum_entries = CurriculumEntryRepository(session)

    def list_all(self) -> Sequence[ClassGroup]:
        return self.class_groups.list_all()

    def get(self, class_group_id: int) -> ClassGroup:
        class_group = self.class_groups.get(class_group_id)
        if class_group is None:
            raise NotFoundError(f"ClassGroup {class_group_id} not found")
        return class_group

    def _ensure_tutor_exists(self, tutor_id: int | None) -> None:
        if tutor_id is not None and self.teachers.get(tutor_id) is None:
            raise NotFoundError(f"Teacher {tutor_id} not found")

    def _ensure_room_exists(self, home_room_id: int | None) -> None:
        if home_room_id is not None and self.rooms.get(home_room_id) is None:
            raise NotFoundError(f"Room {home_room_id} not found")

    def create(self, payload: ClassGroupCreate) -> ClassGroup:
        if self.class_groups.get_by_name(payload.name) is not None:
            raise ConflictError(f"A class group with name {payload.name} already exists")
        self._ensure_tutor_exists(payload.tutor_id)
        self._ensure_room_exists(payload.home_room_id)

        class_group = ClassGroup(**payload.model_dump())
        self.class_groups.add(class_group)
        self.session.commit()
        self.session.refresh(class_group)
        return class_group

    def update(self, class_group_id: int, payload: ClassGroupUpdate) -> ClassGroup:
        class_group = self.get(class_group_id)
        changes = payload.model_dump(exclude_unset=True)

        new_name = changes.get("name")
        if (
            new_name is not None
            and new_name != class_group.name
            and self.class_groups.get_by_name(new_name) is not None
        ):
            raise ConflictError(f"A class group with name {new_name} already exists")

        if "tutor_id" in changes:
            self._ensure_tutor_exists(changes["tutor_id"])
        if "home_room_id" in changes:
            self._ensure_room_exists(changes["home_room_id"])

        for field, value in changes.items():
            setattr(class_group, field, value)
        self.session.commit()
        self.session.refresh(class_group)
        return class_group

    def delete(self, class_group_id: int) -> None:
        class_group = self.get(class_group_id)
        if self.curriculum_entries.exists_for_class_group(class_group_id):
            raise ConflictError(f"ClassGroup {class_group_id} has curriculum entries")
        self.class_groups.delete(class_group)
        self.session.commit()
