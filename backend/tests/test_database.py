"""The database must enforce what the schema declares."""

from sqlalchemy import text
from sqlalchemy.orm import Session


def test_sqlite_enforces_foreign_keys(session: Session) -> None:
    """SQLite ignores foreign keys unless each connection turns them on.

    Without this every ``ForeignKey`` and ``ON DELETE CASCADE`` in the models is
    decorative, and a deleted row can leave dangling references behind.
    """
    assert session.execute(text("PRAGMA foreign_keys")).scalar() == 1
