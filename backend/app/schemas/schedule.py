"""Schedule request and response models.

The read models are shaped for the weekly grid: a session row already carries
every label the UI paints (group, subject, teacher, room, day and period), so the
frontend never has to join several endpoints to render a cell.
"""

from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ScheduleStatus
from app.solver.model import SolverStatus


class ScheduleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ScheduleRead(BaseModel):
    """A schedule without its sessions, for listings."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: ScheduleStatus
    created_at: datetime
    generated_at: datetime | None = None
    solver_status: str | None = None


class ScheduledSessionRead(BaseModel):
    """One cell of the weekly grid, denormalised for display."""

    id: int
    curriculum_entry_id: int
    class_group_id: int
    class_group_name: str
    subject_id: int
    subject_code: str
    subject_name: str
    teacher_id: int
    teacher_name: str
    room_id: int | None = None
    room_name: str | None = None
    time_slot_id: int
    day_of_week: int
    period_index: int
    start_time: time
    end_time: time
    locked: bool


class ScheduleDetail(ScheduleRead):
    """A schedule with every placed session, ordered day by day."""

    sessions: list[ScheduledSessionRead] = []


class ScheduledSessionUpdate(BaseModel):
    """A manual edit: move the session, change its room or pin it.

    Only the fields present in the request are applied, so ``room_id: null``
    clears the room while omitting ``room_id`` leaves it untouched.
    """

    time_slot_id: int | None = None
    room_id: int | None = None
    locked: bool | None = None


class GenerationResult(BaseModel):
    """What a solver run did, whether or not it found a timetable."""

    schedule_id: int
    solver_status: SolverStatus
    solved: bool
    # Sessions written by this run. Zero when the solver found nothing, in which
    # case the previously stored timetable is left untouched.
    sessions_placed: int
    # Weighted cost of the soft constraints the solver had to break.
    penalty: int | None = None
    message: str = ""
    generated_at: datetime | None = None


class ConflictRead(BaseModel):
    """One hard-constraint violation found in a stored timetable."""

    code: str
    message: str
    entry_ids: list[int] = []
    slot_id: int | None = None


class ConflictReport(BaseModel):
    schedule_id: int
    has_conflicts: bool
    conflicts: list[ConflictRead] = []
