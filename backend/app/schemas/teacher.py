"""Teacher request and response models.

Reference implementation: every other entity's schemas follow this shape.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TeacherBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    is_specialist: bool = False
    max_periods_per_week: int = Field(default=25, ge=1, le=40)
    active: bool = True


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    """Every field optional: this is a partial update."""

    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    is_specialist: bool | None = None
    max_periods_per_week: int | None = Field(default=None, ge=1, le=40)
    active: bool | None = None


class TeacherRead(TeacherBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
