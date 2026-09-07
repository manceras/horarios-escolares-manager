"""Telling the user a new version exists, and installing it on request."""

from fastapi import APIRouter

from app.api.responses import ERROR_RESPONSES
from app.core.errors import ConflictError
from app.desktop import updates
from app.schemas.common import Message
from app.schemas.update import UpdateStatusRead

router = APIRouter(prefix="/updates", tags=["updates"], responses=ERROR_RESPONSES)


@router.get("", response_model=UpdateStatusRead)
def read_update_status() -> UpdateStatusRead:
    status = updates.check_for_update()
    return UpdateStatusRead(
        current_version=status.current_version,
        latest_version=status.latest_version,
        update_available=status.update_available,
        can_install=status.update_available and updates.can_install(),
    )


@router.post("/install", response_model=Message)
def install_update() -> Message:
    """Download the new installer, check it, and hand over to it.

    Returns as soon as the installer is launched. It closes this program, swaps
    the files and starts it again, so the window disappearing is the success
    case, not a crash.
    """
    status = updates.check_for_update()
    if not status.update_available or status.download_url is None:
        raise ConflictError("There is no update to install")
    if not updates.can_install():
        raise ConflictError("This build cannot install updates by itself")

    installer = updates.download_installer(status.download_url)
    updates.run_installer(installer)
    return Message(message=f"Installing {status.latest_version}")
