"""TeacherUnavailability endpoints."""

from collections.abc import Sequence

from fastapi import APIRouter, status

from app.api.deps import TeacherUnavailabilityServiceDep
from app.api.responses import ERROR_RESPONSES
from app.models.school import TeacherUnavailability
from app.schemas.teacher_unavailability import (
    TeacherUnavailabilityCreate,
    TeacherUnavailabilityRead,
    TeacherUnavailabilityReplace,
)

router = APIRouter(
    prefix="/teacher-unavailabilities",
    tags=["teacher-unavailabilities"],
    responses=ERROR_RESPONSES,
)


@router.get("", response_model=list[TeacherUnavailabilityRead])
def list_teacher_unavailabilities(
    service: TeacherUnavailabilityServiceDep,
    teacher_id: int | None = None,
) -> Sequence[TeacherUnavailability]:
    return service.list_all(teacher_id)


@router.post("", response_model=TeacherUnavailabilityRead, status_code=status.HTTP_201_CREATED)
def create_teacher_unavailability(
    payload: TeacherUnavailabilityCreate, service: TeacherUnavailabilityServiceDep
) -> TeacherUnavailability:
    return service.create(payload)


@router.delete("/{unavailability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher_unavailability(
    unavailability_id: int, service: TeacherUnavailabilityServiceDep
) -> None:
    service.delete(unavailability_id)


@router.put("/teacher/{teacher_id}", response_model=list[TeacherUnavailabilityRead])
def replace_teacher_unavailabilities(
    teacher_id: int,
    payload: TeacherUnavailabilityReplace,
    service: TeacherUnavailabilityServiceDep,
) -> Sequence[TeacherUnavailability]:
    return service.replace_for_teacher(teacher_id, payload.time_slot_ids)
