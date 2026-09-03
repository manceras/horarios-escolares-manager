"""What each group has to study, with whom and how often."""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.school import ClassGroup, Subject, Teacher


class CurriculumEntry(Base):
    """The solver's input unit: group X studies subject Y with teacher Z, N times a week."""

    __tablename__ = "curriculum_entries"
    __table_args__ = (
        UniqueConstraint("class_group_id", "subject_id", name="uq_curriculum_group_subject"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    class_group_id: Mapped[int] = mapped_column(ForeignKey("class_groups.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    periods_per_week: Mapped[int] = mapped_column(Integer)

    class_group: Mapped[ClassGroup] = relationship()
    subject: Mapped[Subject] = relationship()
    teacher: Mapped[Teacher] = relationship()
