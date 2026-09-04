# backend/CLAUDE.md

FastAPI + SQLAlchemy 2.0 + SQLite + OR-Tools. Read the root `CLAUDE.md` first.

## Layers — never skip one, never import upwards

```
app/api/v1/*.py       HTTP: path, auth dependency, response model, delegate
app/schemas/*.py      Pydantic in/out models
app/services/*.py     business rules, invariants, transactions
app/repositories/*.py queries for one aggregate
app/models/*.py       SQLAlchemy tables
app/solver/           pure timetable generation, no DB, no FastAPI
app/core/             config, db session, security, errors, settings
```

`app/api/v1/teachers.py` + `app/services/teacher_service.py` +
`app/repositories/teacher_repository.py` + `app/schemas/teacher.py` +
`tests/test_teachers.py` are the reference slice. Copy them.

## Non-negotiables

- `mypy --strict` passes. Every signature is typed, including `-> None`.
- Routers contain no business logic and no ORM queries.
- Services raise `NotFoundError` / `ConflictError` / `ValidationError` from
  `app/core/errors.py`. `HTTPException` only ever appears under `app/api/`.
- Services own `session.commit()`. Repositories only `flush()`.
- The solver imports nothing from `app.models`, `app.core.db` or `fastapi`.
- New model → import it in `app/models/__init__.py` → create a migration.
- Any change to a route or a schema → `make gen-api` from the repo root.

## Traps found the hard way

- **Enum columns come back as plain `str`.** `Schedule.status`, `Room.room_type`
  and friends are stored through `String`, so SQLAlchemy returns `"draft"`, not
  `ScheduleStatus.DRAFT`. Compare with `==`, never with `is`.
- **Cross-aggregate checks live in the service.** Refusing to delete a room that
  a class group still uses means querying another aggregate's table. Do it in the
  service, not by adding foreign-entity methods to the entity's own repository.
- **Order routes before path parameters.** `GET /curriculum-entries/workload`
  must be declared before `GET /curriculum-entries/{entry_id}`, or the int path
  parameter swallows it.

## Commands

```sh
uv sync                       # install dependencies
uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check . --fix && uv run ruff format .
uv run mypy app
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "add rooms"
uv run python scripts/seed.py         # development data
```

## Tests

`tests/` mirrors `app/`. Use the `session` and `client` fixtures from
`conftest.py`; `client` is already authenticated as an admin, so tests focus on
behaviour rather than on tokens. Required for solver constraints, service
invariants and bug fixes.

## Solver

`app/solver/` is deliberately isolated behind the `TimetableSolver` protocol.

- `model.py` — frozen dataclasses in and out.
- `cpsat.py` — the OR-Tools CP-SAT implementation.
- `validation.py` — `find_conflicts()`, the independent check that a timetable is
  valid. Use it in tests and when a human edits a schedule by hand.

Hard constraints make a solution valid. Soft constraints are weighted penalties
in the objective. When you add a constraint: add it to `docs/domain-model.md`,
implement it in `cpsat.py`, check it in `validation.py`, and test it.
