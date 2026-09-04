"""Every v1 router is registered here."""

from fastapi import APIRouter

from app.api.v1 import auth, rooms, subjects, teachers

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(rooms.router)
api_router.include_router(subjects.router)
api_router.include_router(teachers.router)
