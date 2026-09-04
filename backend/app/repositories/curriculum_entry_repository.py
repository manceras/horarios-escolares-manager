"""Persistence for :class:`~app.models.curriculum.CurriculumEntry`.

Curriculum entries are not exposed through their own CRUD slice yet; this
repository only supports the reference check ``ClassGroupService`` needs
before deleting a group.
"""

from sqlalchemy import select

from app.models.curriculum import CurriculumEntry
from app.repositories.base import BaseRepository


class CurriculumEntryRepository(BaseRepository[CurriculumEntry]):
    model = CurriculumEntry

    def exists_for_class_group(self, class_group_id: int) -> bool:
        result = self.session.execute(
            select(CurriculumEntry.id)
            .where(CurriculumEntry.class_group_id == class_group_id)
            .limit(1)
        ).first()
        return result is not None
