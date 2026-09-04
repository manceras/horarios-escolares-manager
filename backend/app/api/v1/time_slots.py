"""TimeSlot endpoints."""

from collections.abc import Sequence

from fastapi import APIRouter, status

from app.api.deps import AnyUser, StaffUser, TimeSlotServiceDep
from app.api.responses import ERROR_RESPONSES
from app.models.school import TimeSlot
from app.schemas.time_slot import TimeSlotCreate, TimeSlotRead, TimeSlotUpdate

router = APIRouter(prefix="/time-slots", tags=["time-slots"], responses=ERROR_RESPONSES)


@router.get("", response_model=list[TimeSlotRead])
def list_time_slots(service: TimeSlotServiceDep, _user: AnyUser) -> Sequence[TimeSlot]:
    return service.list_all()


@router.get("/{time_slot_id}", response_model=TimeSlotRead)
def get_time_slot(time_slot_id: int, service: TimeSlotServiceDep, _user: AnyUser) -> TimeSlot:
    return service.get(time_slot_id)


@router.post("", response_model=TimeSlotRead, status_code=status.HTTP_201_CREATED)
def create_time_slot(
    payload: TimeSlotCreate, service: TimeSlotServiceDep, _user: StaffUser
) -> TimeSlot:
    return service.create(payload)


@router.patch("/{time_slot_id}", response_model=TimeSlotRead)
def update_time_slot(
    time_slot_id: int, payload: TimeSlotUpdate, service: TimeSlotServiceDep, _user: StaffUser
) -> TimeSlot:
    return service.update(time_slot_id, payload)


@router.delete("/{time_slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_slot(time_slot_id: int, service: TimeSlotServiceDep, _user: StaffUser) -> None:
    service.delete(time_slot_id)
