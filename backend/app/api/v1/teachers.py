"""Teacher endpoints.

Reference router: routing, authorisation and delegation only. No business rules.
"""

from collections.abc import Sequence

from fastapi import APIRouter, status

from app.api.deps import AnyUser, StaffUser, TeacherServiceDep
from app.models.school import Teacher
from app.schemas.teacher import TeacherCreate, TeacherRead, TeacherUpdate

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.get("", response_model=list[TeacherRead])
def list_teachers(service: TeacherServiceDep, _user: AnyUser) -> Sequence[Teacher]:
    return service.list_all()


@router.get("/{teacher_id}", response_model=TeacherRead)
def get_teacher(teacher_id: int, service: TeacherServiceDep, _user: AnyUser) -> Teacher:
    return service.get(teacher_id)


@router.post("", response_model=TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(payload: TeacherCreate, service: TeacherServiceDep, _user: StaffUser) -> Teacher:
    return service.create(payload)


@router.patch("/{teacher_id}", response_model=TeacherRead)
def update_teacher(
    teacher_id: int, payload: TeacherUpdate, service: TeacherServiceDep, _user: StaffUser
) -> Teacher:
    return service.update(teacher_id, payload)


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, service: TeacherServiceDep, _user: StaffUser) -> None:
    service.delete(teacher_id)
