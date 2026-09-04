"""TeacherUnavailability request and response models.

There is no ``TeacherUnavailabilityUpdate``: a slot is either blocked or not,
so an edit is a create or a delete, never a partial update.
"""

from pydantic import BaseModel, ConfigDict, Field


class TeacherUnavailabilityBase(BaseModel):
    teacher_id: int
    time_slot_id: int
    reason: str | None = Field(default=None, max_length=200)


class TeacherUnavailabilityCreate(TeacherUnavailabilityBase):
    pass


class TeacherUnavailabilityRead(TeacherUnavailabilityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TeacherUnavailabilityReplace(BaseModel):
    """The full set of blocked slots for one teacher, replacing whatever existed."""

    time_slot_ids: list[int]
