"""Persistence for :class:`~app.models.school.Room`.

Rooms are not exposed through their own CRUD slice yet; this repository only
supports the existence check ``ClassGroupService`` needs for ``home_room_id``.
"""

from app.models.school import Room
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    model = Room
