"""TimeSlot request and response models.

``day_of_week`` range and ``start_time`` / ``end_time`` ordering are cross-field
or domain-specific rules, so they are validated in the service (raising
``ValidationError``) rather than in the schema.
"""

from datetime import time

from pydantic import BaseModel, ConfigDict


class TimeSlotBase(BaseModel):
    day_of_week: int
    period_index: int
    start_time: time
    end_time: time
    is_break: bool = False


class TimeSlotCreate(TimeSlotBase):
    pass


class TimeSlotUpdate(BaseModel):
    """Every field optional: this is a partial update."""

    day_of_week: int | None = None
    period_index: int | None = None
    start_time: time | None = None
    end_time: time | None = None
    is_break: bool | None = None


class TimeSlotRead(TimeSlotBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
