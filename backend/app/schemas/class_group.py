"""ClassGroup request and response models."""

from pydantic import BaseModel, ConfigDict, Field


class ClassGroupBase(BaseModel):
    name: str = Field(min_length=1, max_length=16)
    grade: int = Field(ge=1, le=6)
    tutor_id: int | None = None
    home_room_id: int | None = None


class ClassGroupCreate(ClassGroupBase):
    pass


class ClassGroupUpdate(BaseModel):
    """Every field optional: this is a partial update."""

    name: str | None = Field(default=None, min_length=1, max_length=16)
    grade: int | None = Field(default=None, ge=1, le=6)
    tutor_id: int | None = None
    home_room_id: int | None = None


class ClassGroupRead(ClassGroupBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
