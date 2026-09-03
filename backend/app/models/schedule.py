"""Generated timetables and their placed sessions."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.curriculum import CurriculumEntry
from app.models.enums import ScheduleStatus
from app.models.school import Room, TimeSlot


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    status: Mapped[ScheduleStatus] = mapped_column(String(16), default=ScheduleStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    solver_status: Mapped[str | None] = mapped_column(String(32), default=None)

    sessions: Mapped[list["ScheduledSession"]] = relationship(
        back_populates="schedule", cascade="all, delete-orphan"
    )


class ScheduledSession(Base):
    """One curriculum entry placed in a time slot and a room."""

    __tablename__ = "scheduled_sessions"
    __table_args__ = (
        UniqueConstraint(
            "schedule_id",
            "curriculum_entry_id",
            "time_slot_id",
            name="uq_session_schedule_entry_slot",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"))
    curriculum_entry_id: Mapped[int] = mapped_column(ForeignKey("curriculum_entries.id"))
    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id"))
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), default=None)
    # A locked session was pinned by a human and survives any later solver run.
    locked: Mapped[bool] = mapped_column(Boolean, default=False)

    schedule: Mapped[Schedule] = relationship(back_populates="sessions")
    curriculum_entry: Mapped[CurriculumEntry] = relationship()
    time_slot: Mapped[TimeSlot] = relationship()
    room: Mapped[Room | None] = relationship()
