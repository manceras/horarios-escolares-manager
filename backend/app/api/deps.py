"""Shared FastAPI dependencies: the database session and one factory per service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.services.class_group_service import ClassGroupService
from app.services.curriculum_service import CurriculumEntryService
from app.services.room_service import RoomService
from app.services.schedule_service import ScheduleService
from app.services.subject_service import SubjectService
from app.services.teacher_service import TeacherService
from app.services.teacher_unavailability_service import TeacherUnavailabilityService
from app.services.time_slot_service import TimeSlotService

SessionDep = Annotated[Session, Depends(get_session)]


def get_teacher_service(session: SessionDep) -> TeacherService:
    return TeacherService(session)


def get_room_service(session: SessionDep) -> RoomService:
    return RoomService(session)


def get_subject_service(session: SessionDep) -> SubjectService:
    return SubjectService(session)


def get_class_group_service(session: SessionDep) -> ClassGroupService:
    return ClassGroupService(session)


def get_time_slot_service(session: SessionDep) -> TimeSlotService:
    return TimeSlotService(session)


def get_teacher_unavailability_service(session: SessionDep) -> TeacherUnavailabilityService:
    return TeacherUnavailabilityService(session)


def get_curriculum_service(session: SessionDep) -> CurriculumEntryService:
    return CurriculumEntryService(session)


def get_schedule_service(session: SessionDep) -> ScheduleService:
    return ScheduleService(session)


TeacherServiceDep = Annotated[TeacherService, Depends(get_teacher_service)]
RoomServiceDep = Annotated[RoomService, Depends(get_room_service)]
SubjectServiceDep = Annotated[SubjectService, Depends(get_subject_service)]
ClassGroupServiceDep = Annotated[ClassGroupService, Depends(get_class_group_service)]
TimeSlotServiceDep = Annotated[TimeSlotService, Depends(get_time_slot_service)]
TeacherUnavailabilityServiceDep = Annotated[
    TeacherUnavailabilityService, Depends(get_teacher_unavailability_service)
]
CurriculumServiceDep = Annotated[CurriculumEntryService, Depends(get_curriculum_service)]
ScheduleServiceDep = Annotated[ScheduleService, Depends(get_schedule_service)]
