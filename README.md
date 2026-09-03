# horarios-escolares-manager

Open-source timetable planner for primary schools.

Building a school timetable by hand takes a head of studies days of work and
still ends up with a teacher booked in two classrooms at once. This project
models the school — teachers, groups, subjects, rooms and weekly load — and
generates a conflict-free timetable with a constraint solver, then lets staff
review, adjust and print it.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/manceras/horarios-escolares-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/manceras/horarios-escolares-manager/actions/workflows/ci.yml)

[Léeme en español](README.es.md)

## Status

**Early foundation, not production-ready.** What works today:

- [x] Domain model, migrations and seed data for a Spanish primary school
- [x] Constraint solver (OR-Tools CP-SAT) with the hard constraints below, tested
- [x] Independent timetable validator (`find_conflicts`) for manual edits
- [x] JWT authentication with `admin` / `head_of_studies` / `teacher` roles
- [x] REST API and web UI for teachers, as the reference vertical slice
- [ ] CRUD for groups, subjects, rooms, time slots and curriculum entries
- [ ] Endpoints to run the solver and persist a generated schedule
- [ ] Weekly grid UI with drag-and-drop and live conflict feedback
- [ ] Printable and exportable views per teacher, group and room

Follow the issues if you want to help with any of the unchecked items.

## Constraints the solver understands

Hard constraints — a timetable that breaks one of these is rejected:

- a teacher, a group and a room are each in at most one place per period
- teachers are never scheduled when they are unavailable (part-time, other duties)
- subjects that need a specific space (gym, music room, computer lab) get one
- every curriculum entry gets exactly its weekly number of periods
- nothing is scheduled during break time
- no teacher exceeds their weekly teaching load

Soft constraints — minimised, not guaranteed:

- avoid two sessions of the same subject for the same group on the same day

See [`docs/domain-model.md`](docs/domain-model.md) for the full model.

## Stack

| | |
|---|---|
| Backend | FastAPI, SQLAlchemy 2.0, SQLite, Alembic, OR-Tools CP-SAT |
| Frontend | Vite, React 19, TypeScript (strict), Tailwind v4, shadcn/ui, TanStack Query |
| Tooling | uv, ruff, mypy --strict, ESLint, Prettier, pre-commit, GitHub Actions |
| Deployment | Docker Compose |

The frontend API client is generated from the backend's OpenAPI document, so the
contract cannot drift unnoticed.

## Quick start

Requirements: Python 3.12+ with [uv](https://docs.astral.sh/uv/), Node 22+ with
pnpm, and Docker if you want the container deployment.

```sh
git clone https://github.com/manceras/horarios-escolares-manager.git
cd horarios-escolares-manager
make setup
cp backend/.env.example backend/.env
make migrate
make seed          # development data: admin@example.org / changeme
make dev           # API on :8000, web on :5173
```

Interactive API docs: <http://localhost:8000/docs>.

## Deployment

```sh
cp .env.example .env      # set a real SECRET_KEY
docker compose up -d --build
```

The web app is served on port 8080 and proxies `/api` to the API container. The
SQLite database lives in the `api-data` volume — back it up.

## Everyday commands

```sh
make check      # lint, types and tests for both sides. Run before every commit
make fix        # auto-fix formatting and lint
make gen-api    # regenerate the frontend client after an API change
make migration name=add_rooms
```

## Contributing

Contributions are welcome, especially from people who actually build school
timetables. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and
[`docs/vertical-slice.md`](docs/vertical-slice.md), which walks through adding a
feature end to end.

Code, comments, documentation and commit messages are written in English.
User-facing text is Spanish and lives only in `frontend/src/locales/es.json`.

## License

[MIT](LICENSE) © Antonio Mancera Gamez
