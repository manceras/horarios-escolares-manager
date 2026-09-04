"""Every v1 router is registered here."""

from fastapi import APIRouter

from app.api.v1 import auth, curriculum_entries, teachers

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(curriculum_entries.router)
api_router.include_router(teachers.router)
