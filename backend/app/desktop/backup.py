"""Automatic backups of the desktop database.

The single most likely way for a school to lose a year's timetable is not a bug
in this program: it is a disk that dies, or somebody who deletes the wrong
thing and only notices in September. So the application takes a copy of the
database every time it starts, before it touches the schema, and keeps the last
few. They are plain ``.db`` files; restoring one means renaming it.
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from app.desktop.paths import backup_dir, database_path

logger = logging.getLogger(__name__)

BACKUPS_KEPT = 10
BACKUP_FILE_PREFIX = "horarios-"


def create_backup(source: Path | None = None, destination_dir: Path | None = None) -> Path | None:
    """Copy the database aside. Returns the backup path, or None if there is
    nothing to back up yet.

    Uses SQLite's own backup API rather than copying the file: a plain copy of a
    database with an open write transaction is a corrupt database.
    """
    source = source or database_path()
    if not source.exists():
        return None

    destination_dir = destination_dir or backup_dir()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = destination_dir / f"{BACKUP_FILE_PREFIX}{stamp}.db"

    with sqlite3.connect(source) as origin, sqlite3.connect(destination) as copy:
        origin.backup(copy)

    logger.info("Wrote backup %s", destination)
    return destination


def prune_backups(destination_dir: Path | None = None, keep: int = BACKUPS_KEPT) -> list[Path]:
    """Delete all but the newest ``keep`` backups. Returns what was deleted."""
    destination_dir = destination_dir or backup_dir()
    backups = sorted(
        destination_dir.glob(f"{BACKUP_FILE_PREFIX}*.db"),
        key=lambda path: path.name,
        reverse=True,
    )

    removed = []
    for stale in backups[keep:]:
        stale.unlink(missing_ok=True)
        removed.append(stale)
    return removed


def back_up_and_prune() -> Path | None:
    """The startup routine: one backup, then keep the directory bounded.

    A failed backup must never stop the program from opening -- a school that
    cannot print tomorrow's timetable because a backup failed is worse off than
    one running without today's copy. The failure is logged and swallowed.
    """
    try:
        backup = create_backup()
        prune_backups()
        return backup
    except (OSError, sqlite3.Error):
        logger.exception("Could not back up the database; continuing without one")
        return None
