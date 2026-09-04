"""CurriculumEntry request and response models."""

from pydantic import BaseModel, ConfigDict, Field


class CurriculumEntryBase(BaseModel):
    class_group_id: int
    subject_id: int
    teacher_id: int
    periods_per_week: int = Field(ge=1)


class CurriculumEntryCreate(CurriculumEntryBase):
    pass


class CurriculumEntryUpdate(BaseModel):
    """Every field optional: this is a partial update."""

    class_group_id: int | None = None
    subject_id: int | None = None
    teacher_id: int | None = None
    periods_per_week: int | None = Field(default=None, ge=1)


class CurriculumEntryRead(CurriculumEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CurriculumEntryDetail(BaseModel):
    """A curriculum entry with the related names resolved, ready for a UI table."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    class_group_id: int
    subject_id: int
    teacher_id: int
    periods_per_week: int
    class_group_name: str
    subject_code: str
    subject_name: str
    teacher_name: str


class GroupWorkload(BaseModel):
    """How many periods a class group has assigned versus its available slots."""

    class_group_id: int
    class_group_name: str
    assigned_periods: int
    available_periods: int
    fits: bool


class TeacherWorkload(BaseModel):
    """How many periods a teacher has assigned versus their weekly maximum."""

    teacher_id: int
    teacher_name: str
    assigned_periods: int
    max_periods_per_week: int
    fits: bool


class WorkloadReport(BaseModel):
    groups: list[GroupWorkload]
    teachers: list[TeacherWorkload]
