# Architecture

Two deployable pieces in one repository. The browser talks to the API over HTTP
only; there is no shared runtime code between them, only a generated type
contract.

```
┌──────────────────────────┐        ┌────────────────────────────────────┐
│ frontend (Vite + React)  │        │ backend (FastAPI)                  │
│                          │  HTTP  │                                    │
│ routes → features → api  │ ─────► │ api/v1 → services → repositories   │
│         TanStack Query   │  JSON  │                    → models (ORM)  │
│         generated client │ ◄───── │            solver/ (OR-Tools)      │
└──────────────────────────┘        └──────────────┬─────────────────────┘
             ▲                                     │
             │ openapi.json → make gen-api         ▼
             └──────────────────────────────  SQLite (file)
```

## Backend layers

Dependencies point downwards only. A layer never imports from the layer above it.

| Layer | Directory | Owns | Must not |
|---|---|---|---|
| API | `app/api/v1/` | HTTP routing, auth dependencies, status codes | Contain business rules or touch the ORM session directly |
| Schemas | `app/schemas/` | Pydantic request/response models | Import SQLAlchemy models |
| Services | `app/services/` | Business rules, invariants, transactions, orchestration | Know about HTTP (no `HTTPException`, raise domain errors) |
| Repositories | `app/repositories/` | Queries and persistence for one aggregate | Contain business rules |
| Models | `app/models/` | SQLAlchemy table definitions | Import services or schemas |
| Solver | `app/solver/` | Timetable generation, pure and side-effect free | Touch the database or the session |
| Core | `app/core/` | Config, database session, security, errors, dependencies | Import features |

The solver is deliberately isolated: it receives a plain `SolverInput` dataclass
and returns a `SolverResult`. It can be unit-tested and replaced (see
`docs/adr/0003-cp-sat-solver.md`) without touching anything else.

## Errors

Services raise domain errors from `app/core/errors.py` (`NotFoundError`,
`ConflictError`, `ValidationError`, `PermissionDeniedError`). A single exception
handler in `app/main.py` maps them to HTTP responses with a stable shape:

```json
{ "detail": "Teacher 12 not found", "code": "not_found" }
```

Never raise `HTTPException` outside `app/api/`.

## Frontend layers

| Layer | Directory | Owns |
|---|---|---|
| Routes | `src/routes/` | One file per URL, composition and page layout only |
| Features | `src/features/<name>/` | Components, hooks and forms of one domain area |
| API | `src/lib/api/` | Generated types, typed client, query keys |
| UI | `src/components/ui/` | shadcn/ui primitives — generated, rarely edited by hand |
| Lib | `src/lib/` | Framework-agnostic helpers (dates, formatting, i18n setup) |

Server state lives in TanStack Query. Client state lives in `useState` or a small
context. There is no global store; do not add one without an ADR.

## The API contract

`backend` is the source of truth. `make gen-api` exports `openapi.json` and
regenerates `frontend/src/lib/api/schema.d.ts`. The generated file is
git-ignored and rebuilt in CI, so a drifting contract fails the build instead of
failing in the browser.

## Data

SQLite through SQLAlchemy 2.0 with Alembic migrations. Nothing in the code assumes
SQLite beyond the connection URL, so a move to PostgreSQL is a configuration
change plus a migration review.
