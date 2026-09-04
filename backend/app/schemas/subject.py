"""Subject request and response models."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RoomType


class SubjectBase(BaseModel):
    code: str = Field(min_length=1, max_length=16)
    name: str = Field(min_length=1, max_length=120)
    required_room_type: RoomType | None = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    """Every field optional: this is a partial update."""

    code: str | None = Field(default=None, min_length=1, max_length=16)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    required_room_type: RoomType | None = None


class SubjectRead(SubjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
