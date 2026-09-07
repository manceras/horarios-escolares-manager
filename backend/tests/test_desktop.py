"""Desktop shell: paths, backups and serving the web client."""

import sqlite3
from pathlib import Path

import pytest
from app.api.web_client import mount_web_client
from app.desktop import paths
from app.desktop.backup import create_backup, prune_backups
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_the_data_directory_can_be_overridden(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HORARIOS_DATA_DIR", str(tmp_path / "school"))

    assert paths.data_dir() == tmp_path / "school"
    assert paths.data_dir().is_dir()
    assert paths.database_path() == tmp_path / "school" / "horarios.db"


def test_backing_up_a_missing_database_is_not_an_error(tmp_path: Path) -> None:
    assert create_backup(tmp_path / "absent.db", tmp_path) is None


def test_a_backup_is_a_readable_copy_of_the_database(tmp_path: Path) -> None:
    source = tmp_path / "horarios.db"
    with sqlite3.connect(source) as connection:
        connection.execute("CREATE TABLE teachers (name TEXT)")
        connection.execute("INSERT INTO teachers VALUES ('Ana')")

    backup = create_backup(source, tmp_path)

    assert backup is not None
    rows = sqlite3.connect(backup).execute("SELECT name FROM teachers").fetchall()
    assert rows == [("Ana",)]


def test_pruning_keeps_only_the_newest_backups(tmp_path: Path) -> None:
    for stamp in ("20260101-090000", "20260102-090000", "20260103-090000"):
        (tmp_path / f"horarios-{stamp}.db").touch()

    removed = prune_backups(tmp_path, keep=2)

    assert [path.name for path in removed] == ["horarios-20260101-090000.db"]
    assert sorted(path.name for path in tmp_path.glob("*.db")) == [
        "horarios-20260102-090000.db",
        "horarios-20260103-090000.db",
    ]


@pytest.fixture
def web_client(tmp_path: Path) -> TestClient:
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("console.log('hi')")
    (tmp_path / "index.html").write_text("<!doctype html><title>Horarios</title>")
    (tmp_path / "favicon.ico").write_text("icon")

    app = FastAPI()

    @app.get("/api/v1/teachers")
    def teachers() -> list[str]:
        return []

    mount_web_client(app, tmp_path)
    return TestClient(app)


def test_a_client_route_falls_back_to_the_shell(web_client: TestClient) -> None:
    """Reloading the window on a deep link must not 404: the router is in the browser."""
    response = web_client.get("/schedules/12")

    assert response.status_code == 200
    assert "<!doctype html>" in response.text


def test_real_files_are_served_as_themselves(web_client: TestClient) -> None:
    assert web_client.get("/favicon.ico").text == "icon"
    assert "console.log" in web_client.get("/assets/app.js").text


def test_an_unknown_api_path_stays_a_404(web_client: TestClient) -> None:
    """Without this, a typo in a fetch would silently return the HTML shell."""
    assert web_client.get("/api/v1/absent").status_code == 404
    assert web_client.get("/api/v1/teachers").json() == []


def test_the_web_client_mount_is_optional(tmp_path: Path) -> None:
    """A source checkout with no build must still start; Vite serves the UI there."""
    app = FastAPI()
    mount_web_client(app, tmp_path / "missing")

    assert TestClient(app).get("/anything").status_code == 404
