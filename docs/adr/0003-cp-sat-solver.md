# 3. Timetable generation with OR-Tools CP-SAT

- Status: accepted
- Date: 2026-09-03

## Context

Timetabling is a constraint satisfaction problem. Even a small primary school
(~18 groups, ~25 teachers, 25 weekly periods) has too large a search space for a
hand-rolled search to handle well once soft preferences are added. A hand-written
backtracker degrades badly exactly when constraints get interesting.

Licensing mattered: the project must stay free to run.

## Decision

Use **OR-Tools CP-SAT** (`ortools`, Apache License 2.0 — free for commercial and
non-commercial use, no runtime fees).

The solver sits behind a narrow interface in `app/solver/`:

```python
class TimetableSolver(Protocol):
    def solve(self, data: SolverInput, options: SolverOptions) -> SolverResult: ...
```

`SolverInput` and `SolverResult` are plain dataclasses. The solver never touches
the database or the ORM. Hard constraints make a solution valid; soft constraints
are weighted penalties in the objective.

## Consequences

- `ortools` is a heavy wheel (~100 MB). It is a backend-only dependency and is
  installed in the Docker image.
- Solving runs synchronously with a time limit for now. When schools get large
  enough for that to hurt, move it to a background task — that is a new ADR.
- Because of the Protocol, an alternative implementation (a greedy heuristic for
  tiny inputs, for instance) can be added without touching services or API.
- Locked sessions are modelled as fixed assignments, so a re-run preserves manual
  edits.
