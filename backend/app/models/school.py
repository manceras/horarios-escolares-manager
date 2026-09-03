"""Core school entities: teachers, subjects, groups, rooms and time slots."""

from datetime import time

from sqlalchemy import Boolean, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import RoomType


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    is_specialist: Mapped[bool] = mapped_column(Boolean, default=False)
    max_periods_per_week: Mapped[int] = mapped_column(Integer, default=25)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    unavailabilities: Mapped[list["TeacherUnavailability"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    required_room_type: Mapped[RoomType | None] = mapped_column(String(32), default=None)


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    room_type: Mapped[RoomType] = mapped_column(String(32), default=RoomType.CLASSROOM)
    capacity: Mapped[int] = mapped_column(Integer, default=25)


class ClassGroup(Base):
    __tablename__ = "class_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(16), unique=True)
    grade: Mapped[int] = mapped_column(Integer)
    tutor_id: Mapped[int | None] = mapped_column(ForeignKey("teachers.id"), default=None)
    home_room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), default=None)

    tutor: Mapped[Teacher | None] = relationship()
    home_room: Mapped[Room | None] = relationship()


class TimeSlot(Base):
    """A weekday plus a period within the day. Monday is day 0."""

    __tablename__ = "time_slots"
    __table_args__ = (UniqueConstraint("day_of_week", "period_index", name="uq_slot_day_period"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    day_of_week: Mapped[int] = mapped_column(Integer)
    period_index: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    is_break: Mapped[bool] = mapped_column(Boolean, default=False)


class TeacherUnavailability(Base):
    """A slot in which a teacher cannot teach. Absence of a row means available."""

    __tablename__ = "teacher_unavailabilities"
    __table_args__ = (
        UniqueConstraint("teacher_id", "time_slot_id", name="uq_unavailability_teacher_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id", ondelete="CASCADE"))
    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id", ondelete="CASCADE"))
    reason: Mapped[str | None] = mapped_column(String(200), default=None)

    teacher: Mapped[Teacher] = relationship(back_populates="unavailabilities")
    time_slot: Mapped[TimeSlot] = relationship()
