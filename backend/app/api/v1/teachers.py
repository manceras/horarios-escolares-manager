"""Teacher endpoints.

Reference router: routing, authorisation and delegation only. No business rules.
"""

from collections.abc import Sequence

from fastapi import APIRouter, status

from app.api.deps import TeacherServiceDep
from app.api.responses import ERROR_RESPONSES
from app.models.school import Teacher
from app.schemas.teacher import TeacherCreate, TeacherRead, TeacherUpdate

router = APIRouter(prefix="/teachers", tags=["teachers"], responses=ERROR_RESPONSES)


@router.get("", response_model=list[TeacherRead])
def list_teachers(service: TeacherServiceDep) -> Sequence[Teacher]:
    return service.list_all()


@router.get("/{teacher_id}", response_model=TeacherRead)
def get_teacher(teacher_id: int, service: TeacherServiceDep) -> Teacher:
    return service.get(teacher_id)


@router.post("", response_model=TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(payload: TeacherCreate, service: TeacherServiceDep) -> Teacher:
    return service.create(payload)


@router.patch("/{teacher_id}", response_model=TeacherRead)
def update_teacher(teacher_id: int, payload: TeacherUpdate, service: TeacherServiceDep) -> Teacher:
    return service.update(teacher_id, payload)


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, service: TeacherServiceDep) -> None:
    service.delete(teacher_id)
