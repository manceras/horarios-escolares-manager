"""Business rules for subjects."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.curriculum import CurriculumEntry
from app.models.school import Subject
from app.repositories.subject_repository import SubjectRepository
from app.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.subjects = SubjectRepository(session)

    def list_all(self) -> Sequence[Subject]:
        return self.subjects.list_all()

    def get(self, subject_id: int) -> Subject:
        subject = self.subjects.get(subject_id)
        if subject is None:
            raise NotFoundError(f"Subject {subject_id} not found")
        return subject

    def create(self, payload: SubjectCreate) -> Subject:
        if self.subjects.get_by_code(payload.code) is not None:
            raise ConflictError(f"A subject with code {payload.code} already exists")
        subject = Subject(**payload.model_dump())
        self.subjects.add(subject)
        self.session.commit()
        self.session.refresh(subject)
        return subject

    def update(self, subject_id: int, payload: SubjectUpdate) -> Subject:
        subject = self.get(subject_id)
        changes = payload.model_dump(exclude_unset=True)

        new_code = changes.get("code")
        if new_code is not None and new_code != subject.code:
            existing = self.subjects.get_by_code(new_code)
            if existing is not None:
                raise ConflictError(f"A subject with code {new_code} already exists")

        for field, value in changes.items():
            setattr(subject, field, value)
        self.session.commit()
        self.session.refresh(subject)
        return subject

    def delete(self, subject_id: int) -> None:
        subject = self.get(subject_id)

        used_in_curriculum = self.session.execute(
            select(CurriculumEntry.id).where(CurriculumEntry.subject_id == subject_id)
        ).first()
        if used_in_curriculum is not None:
            raise ConflictError(f"Subject {subject_id} is referenced by a curriculum entry")

        self.subjects.delete(subject)
        self.session.commit()
