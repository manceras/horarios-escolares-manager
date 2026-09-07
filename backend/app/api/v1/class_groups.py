"""ClassGroup endpoints."""

from collections.abc import Sequence

from fastapi import APIRouter, status

from app.api.deps import ClassGroupServiceDep
from app.api.responses import ERROR_RESPONSES
from app.models.school import ClassGroup
from app.schemas.class_group import ClassGroupCreate, ClassGroupRead, ClassGroupUpdate

router = APIRouter(prefix="/class-groups", tags=["class-groups"], responses=ERROR_RESPONSES)


@router.get("", response_model=list[ClassGroupRead])
def list_class_groups(service: ClassGroupServiceDep) -> Sequence[ClassGroup]:
    return service.list_all()


@router.get("/{class_group_id}", response_model=ClassGroupRead)
def get_class_group(class_group_id: int, service: ClassGroupServiceDep) -> ClassGroup:
    return service.get(class_group_id)


@router.post("", response_model=ClassGroupRead, status_code=status.HTTP_201_CREATED)
def create_class_group(payload: ClassGroupCreate, service: ClassGroupServiceDep) -> ClassGroup:
    return service.create(payload)


@router.patch("/{class_group_id}", response_model=ClassGroupRead)
def update_class_group(
    class_group_id: int, payload: ClassGroupUpdate, service: ClassGroupServiceDep
) -> ClassGroup:
    return service.update(class_group_id, payload)


@router.delete("/{class_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class_group(class_group_id: int, service: ClassGroupServiceDep) -> None:
    service.delete(class_group_id)
