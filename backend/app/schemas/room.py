"""Room request and response models."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RoomType


class RoomBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    room_type: RoomType = RoomType.CLASSROOM
    capacity: int = Field(default=25, ge=1)


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    """Every field optional: this is a partial update."""

    name: str | None = Field(default=None, min_length=1, max_length=80)
    room_type: RoomType | None = None
    capacity: int | None = Field(default=None, ge=1)


class RoomRead(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
