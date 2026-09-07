"""Bring the user's database up to date when the program starts.

A school never runs ``alembic upgrade head``. They double-click an icon, and
the version they are opening may be several releases newer than the database
sitting in their profile. Migrating on startup is what makes an update a
download rather than a phone call.
"""

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.desktop.paths import bundle_dir, database_url

logger = logging.getLogger(__name__)


def alembic_config(script_location: Path | None = None, url: str | None = None) -> Config:
    """Build the Alembic configuration without reading ``alembic.ini``.

    The ini file only ever supplied a script location and a fallback URL, and
    shipping it inside a one-file executable is one more thing to get wrong.
    ``alembic/env.py`` tolerates a config with no file behind it.
    """
    config = Config()
    config.set_main_option("script_location", str(script_location or bundle_dir() / "alembic"))
    config.set_main_option("sqlalchemy.url", url or database_url())
    return config


def upgrade_to_head(script_location: Path | None = None, url: str | None = None) -> None:
    """Apply every pending migration. Creates the database if it is missing."""
    logger.info("Upgrading the database schema")
    command.upgrade(alembic_config(script_location, url), "head")
