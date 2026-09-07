"""Serving the built web client from the API process.

The desktop application is one process listening on one loopback port: the API
under ``/api``, and everything else the single-page client. Without the
catch-all below, reloading the window on ``/schedules`` would 404 -- the router
lives in the browser, and the server has never heard of that path.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

INDEX_FILE_NAME = "index.html"


def mount_web_client(app: FastAPI, directory: Path) -> None:
    """Serve ``directory`` as the application UI. Does nothing if it is missing."""
    index = directory / INDEX_FILE_NAME
    if not index.is_file():
        return

    assets = directory / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{requested_path:path}", include_in_schema=False)
    def serve_client(requested_path: str) -> FileResponse:
        # A real file (favicon, manifest, ...) wins; anything else is a client
        # route and gets the shell, which then renders it.
        candidate = (directory / requested_path).resolve()
        if requested_path and candidate.is_file() and candidate.is_relative_to(directory.resolve()):
            return FileResponse(candidate)
        if requested_path.startswith("api/"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return FileResponse(index)
