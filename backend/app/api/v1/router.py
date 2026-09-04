"""Every v1 router is registered here."""

from fastapi import APIRouter

from app.api.v1 import auth, schedules, teachers

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(teachers.router)
api_router.include_router(schedules.router)
