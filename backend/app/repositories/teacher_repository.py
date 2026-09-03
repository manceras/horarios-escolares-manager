"""Persistence for :class:`~app.models.school.Teacher`."""

from sqlalchemy import select

from app.models.school import Teacher
from app.repositories.base import BaseRepository


class TeacherRepository(BaseRepository[Teacher]):
    model = Teacher

    def get_by_email(self, email: str) -> Teacher | None:
        return self.session.execute(
            select(Teacher).where(Teacher.email == email)
        ).scalar_one_or_none()
