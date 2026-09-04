"""Business rules for rooms."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.schedule import ScheduledSession
from app.models.school import ClassGroup, Room
from app.repositories.room_repository import RoomRepository
from app.schemas.room import RoomCreate, RoomUpdate


class RoomService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.rooms = RoomRepository(session)

    def list_all(self) -> Sequence[Room]:
        return self.rooms.list_all()

    def get(self, room_id: int) -> Room:
        room = self.rooms.get(room_id)
        if room is None:
            raise NotFoundError(f"Room {room_id} not found")
        return room

    def create(self, payload: RoomCreate) -> Room:
        if self.rooms.get_by_name(payload.name) is not None:
            raise ConflictError(f"A room named {payload.name} already exists")
        room = Room(**payload.model_dump())
        self.rooms.add(room)
        self.session.commit()
        self.session.refresh(room)
        return room

    def update(self, room_id: int, payload: RoomUpdate) -> Room:
        room = self.get(room_id)
        changes = payload.model_dump(exclude_unset=True)

        new_name = changes.get("name")
        if new_name is not None and new_name != room.name:
            existing = self.rooms.get_by_name(new_name)
            if existing is not None:
                raise ConflictError(f"A room named {new_name} already exists")

        for field, value in changes.items():
            setattr(room, field, value)
        self.session.commit()
        self.session.refresh(room)
        return room

    def delete(self, room_id: int) -> None:
        room = self.get(room_id)

        used_as_home_room = self.session.execute(
            select(ClassGroup.id).where(ClassGroup.home_room_id == room_id)
        ).first()
        if used_as_home_room is not None:
            raise ConflictError(f"Room {room_id} is the home room of a class group")

        used_in_session = self.session.execute(
            select(ScheduledSession.id).where(ScheduledSession.room_id == room_id)
        ).first()
        if used_in_session is not None:
            raise ConflictError(f"Room {room_id} is referenced by a scheduled session")

        self.rooms.delete(room)
        self.session.commit()
