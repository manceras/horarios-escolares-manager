"""Every v1 router is registered here."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    class_groups,
    curriculum_entries,
    rooms,
    schedules,
    subjects,
    teacher_unavailabilities,
    teachers,
    time_slots,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(teachers.router)
api_router.include_router(teacher_unavailabilities.router)
api_router.include_router(class_groups.router)
api_router.include_router(subjects.router)
api_router.include_router(rooms.router)
api_router.include_router(time_slots.router)
api_router.include_router(curriculum_entries.router)
api_router.include_router(schedules.router)
