"""Where the application keeps its files on the user's machine.

Two rules drive every path here:

- The database is never written next to the executable. On Windows the program
  usually lands in a folder the user cannot write to, and an installer or an
  antivirus quarantine would take the school's data with it.
- Everything the user owns lives in one directory, so "copy this folder" is a
  complete backup and a complete migration to another computer.
"""

import os
import sys
from pathlib import Path

APP_DIRECTORY_NAME = "Horarios"
DATABASE_FILE_NAME = "horarios.db"


def is_frozen() -> bool:
    """True when running from a PyInstaller bundle rather than from source."""
    return getattr(sys, "frozen", False) is True


def bundle_dir() -> Path:
    """The directory holding read-only resources (migrations, the web client).

    PyInstaller unpacks them into a temporary folder it advertises as
    ``sys._MEIPASS``; from source they sit next to the ``app`` package.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        return Path(str(meipass))
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    """The writable directory holding the database and its backups."""
    override = os.environ.get("HORARIOS_DATA_DIR")
    if override:
        directory = Path(override)
    elif sys.platform == "win32":
        # %LOCALAPPDATA% rather than %APPDATA%: the database is a large local
        # file, and a roaming profile would copy it over the network at login.
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        directory = Path(base) / APP_DIRECTORY_NAME
    elif sys.platform == "darwin":
        directory = Path.home() / "Library" / "Application Support" / APP_DIRECTORY_NAME
    else:
        base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        directory = Path(base) / "horarios"

    directory.mkdir(parents=True, exist_ok=True)
    return directory


def database_path() -> Path:
    return data_dir() / DATABASE_FILE_NAME


def database_url() -> str:
    """The SQLAlchemy URL for the desktop database."""
    return f"sqlite:///{database_path()}"


def backup_dir() -> Path:
    directory = data_dir() / "backups"
    directory.mkdir(parents=True, exist_ok=True)
    return directory
