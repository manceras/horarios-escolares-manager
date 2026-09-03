"""Timetable generation.

This package is pure: it takes plain dataclasses in and gives plain dataclasses
out. It must never import the ORM, the database session or FastAPI, so that it
stays unit-testable and replaceable (see docs/adr/0003-cp-sat-solver.md).
"""

from app.solver.base import TimetableSolver
from app.solver.cpsat import CpSatTimetableSolver
from app.solver.model import (
    Assignment,
    EntryRef,
    RoomRef,
    SlotRef,
    SolverInput,
    SolverOptions,
    SolverResult,
    SolverStatus,
    TeacherRef,
)
from app.solver.validation import Conflict, find_conflicts

__all__ = [
    "Assignment",
    "Conflict",
    "CpSatTimetableSolver",
    "EntryRef",
    "RoomRef",
    "SlotRef",
    "SolverInput",
    "SolverOptions",
    "SolverResult",
    "SolverStatus",
    "TeacherRef",
    "TimetableSolver",
    "find_conflicts",
]
