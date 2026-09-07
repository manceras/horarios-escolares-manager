"""Checking for, and installing, a new version.

A school will not visit a releases page. If an update needs them to notice
something, it will not happen, and every fix stays unshipped until somebody
phones. So the program asks GitHub whether it is out of date, says so in the
window, and installs the answer when they click.

Two things make that safe to do unattended:

- The download is checked against the SHA-256 published with the release. A
  truncated download or a hijacked mirror stops here rather than replacing a
  working installation with a broken one.
- The update is the ordinary Windows installer, run silently. Swapping a running
  executable by hand is the pattern antivirus software is built to stop, and it
  leaves no way back when it half-succeeds.
"""

import hashlib
import json
import logging
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from app import __version__
from app.desktop.paths import data_dir, is_frozen

logger = logging.getLogger(__name__)

RELEASES_URL = "https://api.github.com/repos/manceras/horarios-escolares-manager/releases/latest"
CHECKSUM_SUFFIX = ".sha256"
_TIMEOUT_SECONDS = 10.0
_DOWNLOAD_TIMEOUT_SECONDS = 300.0
_VERSION_PATTERN = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)")


@dataclass(frozen=True)
class UpdateStatus:
    current_version: str
    latest_version: str | None
    update_available: bool
    download_url: str | None


def parse_version(raw: str) -> tuple[int, int, int] | None:
    """Turn ``v1.2.3`` or ``1.2.3`` into a comparable tuple."""
    match = _VERSION_PATTERN.match(raw.strip())
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def is_newer(candidate: str, installed: str) -> bool:
    """Whether ``candidate`` is a later release than ``installed``.

    An unparseable version is never newer: a malformed tag must not push an
    upgrade prompt at a school every time they open the program.
    """
    new = parse_version(candidate)
    old = parse_version(installed)
    if new is None or old is None:
        return False
    return new > old


def _installer_asset(release: dict[str, object]) -> str | None:
    """The Windows installer among a release's assets, if it published one."""
    assets = release.get("assets")
    if not isinstance(assets, list):
        return None
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = str(asset.get("name", ""))
        if name.lower().endswith(".exe") and "setup" in name.lower():
            url = asset.get("browser_download_url")
            if isinstance(url, str):
                return url
    return None


def _read_release(url: str) -> object:
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
        return json.loads(response.read())


def check_for_update(url: str = RELEASES_URL) -> UpdateStatus:
    """Ask GitHub for the latest release.

    Never raises: no network, a rate limit or a GitHub outage means the school
    keeps working on the version they have.
    """
    unavailable = UpdateStatus(__version__, None, False, None)
    try:
        release = _read_release(url)
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError):
        logger.info("Could not reach GitHub to check for updates", exc_info=True)
        return unavailable

    if not isinstance(release, dict):
        return unavailable

    tag = str(release.get("tag_name", ""))
    if not is_newer(tag, __version__):
        return UpdateStatus(__version__, tag or None, False, None)

    return UpdateStatus(__version__, tag, True, _installer_asset(release))


def _download(url: str, destination: Path, timeout: float = _DOWNLOAD_TIMEOUT_SECONDS) -> Path:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        destination.write_bytes(response.read())
    return destination


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_installer(download_url: str, destination_dir: Path | None = None) -> Path:
    """Fetch the installer and verify it against its published checksum.

    Raises ``ValueError`` when the checksum does not match, leaving nothing
    behind: a half-downloaded installer that runs is worse than no update.
    """
    destination_dir = destination_dir or data_dir() / "updates"
    destination_dir.mkdir(parents=True, exist_ok=True)
    installer = destination_dir / download_url.rsplit("/", 1)[-1]

    _download(download_url, installer)

    expected = _download(
        download_url + CHECKSUM_SUFFIX, destination_dir / "checksum.txt"
    ).read_text()
    # The file is the output of `sha256sum`: "<digest>  <file name>".
    expected_digest = expected.split()[0].strip().lower()
    actual_digest = sha256_of(installer)
    if actual_digest != expected_digest:
        installer.unlink(missing_ok=True)
        raise ValueError(
            f"The downloaded update does not match its checksum "
            f"(expected {expected_digest}, got {actual_digest})"
        )

    return installer


def can_install() -> bool:
    """Only the packaged Windows build can update itself in place."""
    return is_frozen() and sys.platform == "win32"


def run_installer(installer: Path) -> None:
    """Hand over to the installer and let it close and restart the program.

    ``/SILENT`` shows a progress bar but asks nothing; the school clicked
    "update" already, and a wizard here is just four more chances to get lost.
    """
    if not can_install():
        raise RuntimeError("Updates can only be installed from the packaged Windows build")

    subprocess.Popen(
        [
            str(installer),
            "/SILENT",
            "/CLOSEAPPLICATIONS",
            "/RESTARTAPPLICATIONS",
            "/NORESTART",
        ],
        close_fds=True,
    )
