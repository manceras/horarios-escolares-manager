"""Entry point of the desktop application.

    python -m app.desktop

Everything a school does with this program happens behind a double click, so
this module is deliberately linear: work out where the data lives, copy it
aside, migrate it, serve it, show it.
"""

import logging
import multiprocessing
import os
import sys


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logger = logging.getLogger("app.desktop")

    from app.desktop import paths

    # Settings are read once, on first import of app.core.config, so the
    # environment has to be right before the application is imported at all.
    os.environ.setdefault("DATABASE_URL", paths.database_url())
    os.environ.setdefault("WEB_CLIENT_DIR", str(paths.bundle_dir() / "web"))

    from app.desktop import migrations, server, window
    from app.desktop.backup import back_up_and_prune

    logger.info("Data directory: %s", paths.data_dir())
    back_up_and_prune()
    migrations.upgrade_to_head()

    from app.main import create_app

    local = server.start(create_app())
    try:
        window.open_window(local.base_url)
    finally:
        local.stop()
    return 0


if __name__ == "__main__":
    # PyInstaller re-executes the bundle for every child process; without this
    # the program would open a new window instead of a worker.
    multiprocessing.freeze_support()
    sys.exit(main())
