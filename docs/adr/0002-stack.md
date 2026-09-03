# 2. Stack: React SPA plus a separate FastAPI backend

- Status: accepted
- Date: 2026-09-03

## Context

A primary school timetable planner. The interesting work is constraint solving,
which is a Python problem (OR-Tools). The interesting UI is a dense, interactive
weekly grid, which is a React problem. The users are a handful of staff on a
school server, not internet scale.

## Decision

Two independent pieces in one repository:

- **backend**: FastAPI, SQLAlchemy 2.0, SQLite, OR-Tools. Managed with `uv`,
  linted with `ruff`, type-checked with `mypy --strict`.
- **frontend**: Vite + React + TypeScript (strict), Tailwind v4 with shadcn/ui
  components, TanStack Query for server state.

The boundary is HTTP. The FastAPI OpenAPI document generates the frontend types,
so the contract cannot drift unnoticed.

Rejected: Next.js (a second backend runtime next to Python buys nothing here);
browser-only storage (staff need shared, backed-up data); Django (heavier than
this domain needs and worse async/OpenAPI support).

## Consequences

- Two toolchains to install; `make setup` and Docker Compose hide it.
- Types are generated, not shared at runtime: `make gen-api` is mandatory after
  any API change, and CI enforces it.
- Auth is explicit (JWT) instead of framework-provided sessions.
