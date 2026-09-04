"""Business rules for curriculum entries -- the solver's input.

A service owns the transaction, enforces the domain rules and raises
:mod:`app.core.errors` -- never ``HTTPException``.
"""

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.models.curriculum import CurriculumEntry
from app.models.school import ClassGroup, Teacher
from app.repositories.curriculum_repository import CurriculumEntryRepository
from app.repositories.teacher_repository import TeacherRepository
from app.schemas.curriculum import (
    CurriculumEntryCreate,
    CurriculumEntryDetail,
    CurriculumEntryUpdate,
    GroupWorkload,
    TeacherWorkload,
    WorkloadReport,
)


class CurriculumEntryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.entries = CurriculumEntryRepository(session)
        self.teachers = TeacherRepository(session)

    def list_all_with_details(self) -> list[CurriculumEntryDetail]:
        return [self._to_detail(entry) for entry in self.entries.list_with_details()]

    def get(self, entry_id: int) -> CurriculumEntry:
        entry = self.entries.get(entry_id)
        if entry is None:
            raise NotFoundError(f"Curriculum entry {entry_id} not found")
        return entry

    def get_detail(self, entry_id: int) -> CurriculumEntryDetail:
        entry = self.entries.get_with_details(entry_id)
        if entry is None:
            raise NotFoundError(f"Curriculum entry {entry_id} not found")
        return self._to_detail(entry)

    def create(self, payload: CurriculumEntryCreate) -> CurriculumEntry:
        class_group = self.entries.get_class_group(payload.class_group_id)
        if class_group is None:
            raise NotFoundError(f"Class group {payload.class_group_id} not found")
        subject = self.entries.get_subject(payload.subject_id)
        if subject is None:
            raise NotFoundError(f"Subject {payload.subject_id} not found")
        teacher = self.teachers.get(payload.teacher_id)
        if teacher is None:
            raise NotFoundError(f"Teacher {payload.teacher_id} not found")

        existing = self.entries.get_by_group_and_subject(payload.class_group_id, payload.subject_id)
        if existing is not None:
            raise ConflictError(
                f"Class group {class_group.name} already has a curriculum entry "
                f"for subject {subject.code}"
            )

        self._check_group_capacity(class_group, payload.periods_per_week)
        self._check_teacher_capacity(teacher, payload.periods_per_week)

        entry = CurriculumEntry(**payload.model_dump())
        self.entries.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def update(self, entry_id: int, payload: CurriculumEntryUpdate) -> CurriculumEntry:
        entry = self.get(entry_id)
        changes = payload.model_dump(exclude_unset=True)

        class_group = entry.class_group
        if "class_group_id" in changes and changes["class_group_id"] != entry.class_group_id:
            new_class_group = self.entries.get_class_group(changes["class_group_id"])
            if new_class_group is None:
                raise NotFoundError(f"Class group {changes['class_group_id']} not found")
            class_group = new_class_group

        subject = entry.subject
        if "subject_id" in changes and changes["subject_id"] != entry.subject_id:
            new_subject = self.entries.get_subject(changes["subject_id"])
            if new_subject is None:
                raise NotFoundError(f"Subject {changes['subject_id']} not found")
            subject = new_subject

        teacher = entry.teacher
        if "teacher_id" in changes and changes["teacher_id"] != entry.teacher_id:
            new_teacher = self.teachers.get(changes["teacher_id"])
            if new_teacher is None:
                raise NotFoundError(f"Teacher {changes['teacher_id']} not found")
            teacher = new_teacher

        if (class_group.id, subject.id) != (entry.class_group_id, entry.subject_id):
            existing = self.entries.get_by_group_and_subject(class_group.id, subject.id)
            if existing is not None and existing.id != entry.id:
                raise ConflictError(
                    f"Class group {class_group.name} already has a curriculum entry "
                    f"for subject {subject.code}"
                )

        periods = changes.get("periods_per_week", entry.periods_per_week)

        group_unchanged = class_group.id == entry.class_group_id
        self._check_group_capacity(
            class_group, periods, exclude_entry_id=entry.id if group_unchanged else None
        )

        teacher_unchanged = teacher.id == entry.teacher_id
        self._check_teacher_capacity(
            teacher, periods, exclude_entry_id=entry.id if teacher_unchanged else None
        )

        for field, value in changes.items():
            setattr(entry, field, value)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def delete(self, entry_id: int) -> None:
        entry = self.get(entry_id)
        if self.entries.has_scheduled_sessions(entry.id):
            raise ConflictError(
                f"Curriculum entry {entry_id} has scheduled sessions and cannot be deleted"
            )
        self.entries.delete(entry)
        self.session.commit()

    def workload(self) -> WorkloadReport:
        available_periods = self.entries.count_non_break_time_slots()
        periods_by_group = self.entries.periods_by_class_group()
        periods_by_teacher = self.entries.periods_by_teacher()

        groups = [
            GroupWorkload(
                class_group_id=group.id,
                class_group_name=group.name,
                assigned_periods=periods_by_group.get(group.id, 0),
                available_periods=available_periods,
                fits=periods_by_group.get(group.id, 0) <= available_periods,
            )
            for group in self.entries.list_all_class_groups()
        ]
        teachers = [
            TeacherWorkload(
                teacher_id=teacher.id,
                teacher_name=teacher.full_name,
                assigned_periods=periods_by_teacher.get(teacher.id, 0),
                max_periods_per_week=teacher.max_periods_per_week,
                fits=periods_by_teacher.get(teacher.id, 0) <= teacher.max_periods_per_week,
            )
            for teacher in self.teachers.list_all()
        ]
        return WorkloadReport(groups=groups, teachers=teachers)

    def _check_group_capacity(
        self, class_group: ClassGroup, added_periods: int, exclude_entry_id: int | None = None
    ) -> None:
        current = self.entries.sum_periods_for_group(
            class_group.id, exclude_entry_id=exclude_entry_id
        )
        total = current + added_periods
        available = self.entries.count_non_break_time_slots()
        if total > available:
            raise ValidationError(
                f"Class group {class_group.name} would have {total} periods assigned, "
                f"but only {available} non-break time slots are available"
            )

    def _check_teacher_capacity(
        self, teacher: Teacher, added_periods: int, exclude_entry_id: int | None = None
    ) -> None:
        current = self.entries.sum_periods_for_teacher(
            teacher.id, exclude_entry_id=exclude_entry_id
        )
        total = current + added_periods
        if total > teacher.max_periods_per_week:
            raise ValidationError(
                f"Teacher {teacher.full_name} would have {total} periods assigned, "
                f"but their maximum is {teacher.max_periods_per_week} periods per week"
            )

    def _to_detail(self, entry: CurriculumEntry) -> CurriculumEntryDetail:
        return CurriculumEntryDetail(
            id=entry.id,
            class_group_id=entry.class_group_id,
            subject_id=entry.subject_id,
            teacher_id=entry.teacher_id,
            periods_per_week=entry.periods_per_week,
            class_group_name=entry.class_group.name,
            subject_code=entry.subject.code,
            subject_name=entry.subject.name,
            teacher_name=entry.teacher.full_name,
        )
