"""Room endpoints. Routing, authorisation and delegation only. No business rules."""

from collections.abc import Sequence

from fastapi import APIRouter, status

from app.api.deps import RoomServiceDep
from app.api.responses import ERROR_RESPONSES
from app.models.school import Room
from app.schemas.room import RoomCreate, RoomRead, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["rooms"], responses=ERROR_RESPONSES)


@router.get("", response_model=list[RoomRead])
def list_rooms(service: RoomServiceDep) -> Sequence[Room]:
    return service.list_all()


@router.get("/{room_id}", response_model=RoomRead)
def get_room(room_id: int, service: RoomServiceDep) -> Room:
    return service.get(room_id)


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, service: RoomServiceDep) -> Room:
    return service.create(payload)


@router.patch("/{room_id}", response_model=RoomRead)
def update_room(room_id: int, payload: RoomUpdate, service: RoomServiceDep) -> Room:
    return service.update(room_id, payload)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, service: RoomServiceDep) -> None:
    service.delete(room_id)
