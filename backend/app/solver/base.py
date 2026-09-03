"""The contract every timetable solver implementation satisfies."""

from typing import Protocol

from app.solver.model import SolverInput, SolverOptions, SolverResult


class TimetableSolver(Protocol):
    """Places every curriculum entry into time slots and rooms.

    Implementations must honour all hard constraints listed in
    ``docs/domain-model.md`` and return ``SolverStatus.INFEASIBLE`` rather than a
    partial solution when they cannot.
    """

    def solve(self, data: SolverInput, options: SolverOptions) -> SolverResult: ...
