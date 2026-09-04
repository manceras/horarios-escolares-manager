"""Persistence for :class:`~app.models.school.Subject`."""

from sqlalchemy import select

from app.models.school import Subject
from app.repositories.base import BaseRepository


class SubjectRepository(BaseRepository[Subject]):
    model = Subject

    def get_by_code(self, code: str) -> Subject | None:
        return self.session.execute(
            select(Subject).where(Subject.code == code)
        ).scalar_one_or_none()
