"""Update availability, as the window reports it."""

from pydantic import BaseModel


class UpdateStatusRead(BaseModel):
    current_version: str
    latest_version: str | None = None
    update_available: bool = False
    # True only in the packaged Windows build: a source checkout updates with git.
    can_install: bool = False
