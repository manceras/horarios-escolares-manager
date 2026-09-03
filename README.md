# horarios

Timetable planner for a primary school. Staff enter teachers, groups, rooms and
the weekly curriculum; the app generates a conflict-free timetable with a
constraint solver and lets them review, adjust and print it.

- **backend** — FastAPI, SQLAlchemy 2.0, SQLite, OR-Tools CP-SAT
- **frontend** — Vite, React 19, TypeScript, Tailwind v4, shadcn/ui, TanStack Query

## Requirements

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node 22+ and pnpm
- Docker (only for the production deployment)

## Getting started

```sh
make setup                     # install everything and the git hooks
cd backend && cp .env.example .env && cd ..
make migrate                   # create the database
make seed                      # development data: admin@example.org / changeme
make dev                       # API on :8000, web on :5173
```

The API documentation is served at http://localhost:8000/docs.

## Everyday commands

```sh
make check      # lint + types + tests, both sides. Run before every commit
make fix        # auto-fix formatting and lint
make gen-api    # regenerate the frontend client after an API change
make migration name=add_rooms
```

## Deployment

```sh
cp .env.example .env    # set a real SECRET_KEY
docker compose up -d --build
```

The web app is served on port 8080 and proxies `/api` to the API container. The
SQLite file lives in the `api-data` volume — back it up.

## Working on this repository

`CLAUDE.md` is the contract every contributor, human or agent, follows. Start
with `docs/vertical-slice.md` to add a feature end to end, and read
`docs/domain-model.md` before touching the data model.

Code, comments, documentation and commit messages are written in **English**.
User-facing text is Spanish and lives only in `frontend/src/locales/es.json`.
