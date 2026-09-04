"""Business rules for teachers.

Reference implementation. A service owns the transaction, enforces the domain
rules and raises :mod:`app.core.errors` -- never ``HTTPException``.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.curriculum import CurriculumEntry
from app.models.school import ClassGroup, Teacher
from app.models.user import User
from app.repositories.teacher_repository import TeacherRepository
from app.schemas.teacher import TeacherCreate, TeacherUpdate


class TeacherService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.teachers = TeacherRepository(session)

    def list_all(self) -> Sequence[Teacher]:
        return self.teachers.list_all()

    def get(self, teacher_id: int) -> Teacher:
        teacher = self.teachers.get(teacher_id)
        if teacher is None:
            raise NotFoundError(f"Teacher {teacher_id} not found")
        return teacher

    def create(self, payload: TeacherCreate) -> Teacher:
        if self.teachers.get_by_email(payload.email) is not None:
            raise ConflictError(f"A teacher with email {payload.email} already exists")
        teacher = Teacher(**payload.model_dump())
        self.teachers.add(teacher)
        self.session.commit()
        self.session.refresh(teacher)
        return teacher

    def update(self, teacher_id: int, payload: TeacherUpdate) -> Teacher:
        teacher = self.get(teacher_id)
        changes = payload.model_dump(exclude_unset=True)

        new_email = changes.get("email")
        if new_email is not None and new_email != teacher.email:
            existing = self.teachers.get_by_email(new_email)
            if existing is not None:
                raise ConflictError(f"A teacher with email {new_email} already exists")

        for field, value in changes.items():
            setattr(teacher, field, value)
        self.session.commit()
        self.session.refresh(teacher)
        return teacher

    def delete(self, teacher_id: int) -> None:
        teacher = self.get(teacher_id)

        teaches = self.session.execute(
            select(CurriculumEntry.id).where(CurriculumEntry.teacher_id == teacher_id)
        ).first()
        if teaches is not None:
            raise ConflictError(f"Teacher {teacher_id} is referenced by a curriculum entry")

        is_tutor = self.session.execute(
            select(ClassGroup.id).where(ClassGroup.tutor_id == teacher_id)
        ).first()
        if is_tutor is not None:
            raise ConflictError(f"Teacher {teacher_id} is the tutor of a class group")

        has_account = self.session.execute(
            select(User.id).where(User.teacher_id == teacher_id)
        ).first()
        if has_account is not None:
            raise ConflictError(f"Teacher {teacher_id} is linked to a user account")

        # Unavailability rows belong to the teacher and are cascaded away with them.
        self.teachers.delete(teacher)
        self.session.commit()
