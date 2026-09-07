"""Entry point of the desktop application.

    python -m app.desktop

Everything a school does with this program happens behind a double click, so
this module is deliberately linear: work out where the data lives, copy it
aside, migrate it, serve it, show it.
"""

import ctypes
import logging
import logging.handlers
import multiprocessing
import os
import sys
from pathlib import Path

LOG_FILE_NAME = "horarios.log"
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 3

logger = logging.getLogger("app.desktop")


def configure_logging(directory: Path) -> Path:
    """Log to a file next to the database.

    The packaged program has no console: without this, a startup failure is a
    window that never appears and a user with nothing to report. The log is
    capped and rotated so it can never fill a school laptop's disk.
    """
    log_file = directory / LOG_FILE_NAME
    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    root.addHandler(logging.StreamHandler())
    return log_file


def report_fatal_error(message: str) -> None:
    """Tell the user something went wrong, in the only place they will look.

    A dialog that names the log file turns "it does not open" into a message
    they can forward.
    """
    sys.stderr.write(f"{message}\n")
    if sys.platform == "win32":
        # MB_ICONERROR | MB_OK
        ctypes.windll.user32.MessageBoxW(None, message, "Horarios", 0x10)  # type: ignore[attr-defined]


def main() -> int:
    from app.desktop import paths

    directory = paths.data_dir()
    log_file = configure_logging(directory)

    try:
        # Settings are read once, on first import of app.core.config, so the
        # environment has to be right before the application is imported at all.
        os.environ.setdefault("DATABASE_URL", paths.database_url())
        os.environ.setdefault("WEB_CLIENT_DIR", str(paths.bundle_dir() / "web"))

        from app.desktop import migrations, server, window
        from app.desktop.backup import back_up_and_prune

        logger.info("Data directory: %s", directory)
        back_up_and_prune()
        migrations.upgrade_to_head()

        from app.main import create_app

        local = server.start(create_app())
        try:
            window.open_window(local.base_url)
        finally:
            local.stop()
    except Exception:
        logger.exception("The application could not start")
        # The only Spanish outside `frontend/src/locales/es.json`, and a
        # deliberate exception to the rule: this fires before the web client
        # exists, so i18n cannot be reached. Keep it to these two lines.
        report_fatal_error(
            "Horarios no ha podido arrancar.\n\n"
            f"Envía este archivo para que podamos ver qué ha pasado:\n{log_file}"
        )
        return 1
    return 0


if __name__ == "__main__":
    # PyInstaller re-executes the bundle for every child process; without this
    # the program would open a new window instead of a worker.
    multiprocessing.freeze_support()
    sys.exit(main())
