"""Persistence for :class:`~app.models.school.ClassGroup`."""

from sqlalchemy import select

from app.models.school import ClassGroup
from app.repositories.base import BaseRepository


class ClassGroupRepository(BaseRepository[ClassGroup]):
    model = ClassGroup

    def get_by_name(self, name: str) -> ClassGroup | None:
        return self.session.execute(
            select(ClassGroup).where(ClassGroup.name == name)
        ).scalar_one_or_none()
