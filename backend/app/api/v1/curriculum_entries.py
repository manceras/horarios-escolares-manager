"""Curriculum entry endpoints.

Routing, authorisation and delegation only. No business rules.
"""

from fastapi import APIRouter, status

from app.api.deps import CurriculumServiceDep
from app.api.responses import ERROR_RESPONSES
from app.models.curriculum import CurriculumEntry
from app.schemas.curriculum import (
    CurriculumEntryCreate,
    CurriculumEntryDetail,
    CurriculumEntryRead,
    CurriculumEntryUpdate,
    WorkloadReport,
)

router = APIRouter(
    prefix="/curriculum-entries", tags=["curriculum-entries"], responses=ERROR_RESPONSES
)


@router.get("", response_model=list[CurriculumEntryDetail])
def list_curriculum_entries(service: CurriculumServiceDep) -> list[CurriculumEntryDetail]:
    return service.list_all_with_details()


@router.get("/workload", response_model=WorkloadReport)
def get_workload(service: CurriculumServiceDep) -> WorkloadReport:
    return service.workload()


@router.get("/{entry_id}", response_model=CurriculumEntryDetail)
def get_curriculum_entry(entry_id: int, service: CurriculumServiceDep) -> CurriculumEntryDetail:
    return service.get_detail(entry_id)


@router.post("", response_model=CurriculumEntryRead, status_code=status.HTTP_201_CREATED)
def create_curriculum_entry(
    payload: CurriculumEntryCreate, service: CurriculumServiceDep
) -> CurriculumEntry:
    return service.create(payload)


@router.patch("/{entry_id}", response_model=CurriculumEntryRead)
def update_curriculum_entry(
    entry_id: int, payload: CurriculumEntryUpdate, service: CurriculumServiceDep
) -> CurriculumEntry:
    return service.update(entry_id, payload)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curriculum_entry(entry_id: int, service: CurriculumServiceDep) -> None:
    service.delete(entry_id)
