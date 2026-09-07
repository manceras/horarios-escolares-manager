"""FastAPI application factory and error handling."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.v1.router import api_router
from app.api.web_client import mount_web_client
from app.core.config import get_settings
from app.core.errors import DomainError


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="horarios API",
        version="0.1.0",
        description="Timetable planner for a primary school",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        """Single place where domain errors become HTTP responses."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(_request: Request, _exc: IntegrityError) -> JSONResponse:
        """A constraint the database refused is the user's conflict, not a crash.

        Services are expected to check references themselves and raise a
        ``ConflictError`` with a useful message. This is the net for the one that
        was forgotten: the client still gets a 409 rather than a 500, and the
        database error itself is never echoed back.
        """
        return JSONResponse(
            status_code=409,
            content={
                "detail": "The request conflicts with data that already exists",
                "code": "conflict",
            },
        )

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router)

    # Registered last: its catch-all would otherwise shadow every API route.
    if settings.web_client_dir:
        mount_web_client(app, Path(settings.web_client_dir))

    return app


app = create_app()
