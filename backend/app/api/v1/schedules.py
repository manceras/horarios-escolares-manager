"""Schedule endpoints: create a draft, generate it, review it, publish it.

Routing, authorisation and delegation only. Generation runs synchronously with a
time limit, a deliberate choice recorded in docs/adr/0003-cp-sat-solver.md.
"""

from collections.abc import Sequence

from fastapi import APIRouter, status

from app.api.deps import AnyUser, ScheduleServiceDep, StaffUser
from app.api.responses import ERROR_RESPONSES
from app.models.schedule import Schedule
from app.schemas.schedule import (
    ConflictReport,
    GenerationResult,
    ScheduleCreate,
    ScheduleDetail,
    ScheduledSessionRead,
    ScheduledSessionUpdate,
    ScheduleRead,
)

router = APIRouter(prefix="/schedules", tags=["schedules"], responses=ERROR_RESPONSES)


@router.get("", response_model=list[ScheduleRead])
def list_schedules(service: ScheduleServiceDep, _user: AnyUser) -> Sequence[Schedule]:
    return service.list_all()


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate, service: ScheduleServiceDep, _user: StaffUser
) -> Schedule:
    return service.create(payload)


@router.get("/{schedule_id}", response_model=ScheduleDetail)
def get_schedule(schedule_id: int, service: ScheduleServiceDep, _user: AnyUser) -> ScheduleDetail:
    return service.get_detail(schedule_id)


@router.get("/{schedule_id}/conflicts", response_model=ConflictReport)
def get_schedule_conflicts(
    schedule_id: int, service: ScheduleServiceDep, _user: AnyUser
) -> ConflictReport:
    return service.find_conflicts(schedule_id)


@router.post("/{schedule_id}/generate", response_model=GenerationResult)
def generate_schedule(
    schedule_id: int, service: ScheduleServiceDep, _user: StaffUser
) -> GenerationResult:
    """Run the solver. An infeasible input is a result, not an error."""
    return service.generate(schedule_id)


@router.patch("/{schedule_id}/sessions/{session_id}", response_model=ScheduledSessionRead)
def update_scheduled_session(
    schedule_id: int,
    session_id: int,
    payload: ScheduledSessionUpdate,
    service: ScheduleServiceDep,
    _user: StaffUser,
) -> ScheduledSessionRead:
    return service.update_session(schedule_id, session_id, payload)


@router.post("/{schedule_id}/publish", response_model=ScheduleRead)
def publish_schedule(schedule_id: int, service: ScheduleServiceDep, _user: StaffUser) -> Schedule:
    return service.publish(schedule_id)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, service: ScheduleServiceDep, _user: StaffUser) -> None:
    service.delete(schedule_id)
