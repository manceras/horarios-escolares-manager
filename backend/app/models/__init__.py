"""Every model must be imported here so Alembic autogenerate can see it."""

from app.models.base import Base
from app.models.curriculum import CurriculumEntry
from app.models.enums import RoomType, ScheduleStatus
from app.models.schedule import Schedule, ScheduledSession
from app.models.school import (
    ClassGroup,
    Room,
    Subject,
    Teacher,
    TeacherUnavailability,
    TimeSlot,
)

__all__ = [
    "Base",
    "ClassGroup",
    "CurriculumEntry",
    "Room",
    "RoomType",
    "Schedule",
    "ScheduleStatus",
    "ScheduledSession",
    "Subject",
    "Teacher",
    "TeacherUnavailability",
    "TimeSlot",
]
