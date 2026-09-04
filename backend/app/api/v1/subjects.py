"""Subject endpoints. Routing, authorisation and delegation only. No business rules."""

from collections.abc import Sequence

from fastapi import APIRouter, status

from app.api.deps import AnyUser, StaffUser, SubjectServiceDep
from app.api.responses import ERROR_RESPONSES
from app.models.school import Subject
from app.schemas.subject import SubjectCreate, SubjectRead, SubjectUpdate

router = APIRouter(prefix="/subjects", tags=["subjects"], responses=ERROR_RESPONSES)


@router.get("", response_model=list[SubjectRead])
def list_subjects(service: SubjectServiceDep, _user: AnyUser) -> Sequence[Subject]:
    return service.list_all()


@router.get("/{subject_id}", response_model=SubjectRead)
def get_subject(subject_id: int, service: SubjectServiceDep, _user: AnyUser) -> Subject:
    return service.get(subject_id)


@router.post("", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
def create_subject(payload: SubjectCreate, service: SubjectServiceDep, _user: StaffUser) -> Subject:
    return service.create(payload)


@router.patch("/{subject_id}", response_model=SubjectRead)
def update_subject(
    subject_id: int, payload: SubjectUpdate, service: SubjectServiceDep, _user: StaffUser
) -> Subject:
    return service.update(subject_id, payload)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, service: SubjectServiceDep, _user: StaffUser) -> None:
    service.delete(subject_id)
