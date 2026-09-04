"""Persistence for :class:`~app.models.school.Room`."""

from sqlalchemy import select

from app.models.school import Room
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    model = Room

    def get_by_name(self, name: str) -> Room | None:
        return self.session.execute(select(Room).where(Room.name == name)).scalar_one_or_none()
