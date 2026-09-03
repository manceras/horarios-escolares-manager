"""Application users and their roles."""

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import UserRole
from app.models.school import Teacher


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(String(32), default=UserRole.TEACHER)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("teachers.id"), default=None)

    teacher: Mapped[Teacher | None] = relationship()
