# CLAUDE.md — horarios

Timetable planner for a Spanish primary school (colegio de primaria). It stores the
school's teachers, groups, rooms and curriculum, generates conflict-free weekly
timetables with a constraint solver, and lets staff review, adjust and print them.

**It ships as a Windows desktop program with no login**, installed and opened by
one non-technical person. Read
[`docs/adr/0006-desktop-application.md`](docs/adr/0006-desktop-application.md)
before you touch anything that assumes a server, a second user or a password —
there are none, on purpose.

Read this file before touching anything. It is the contract every agent follows.

## Golden rules

1. **English only, everywhere.** Identifiers, comments, docstrings, file names,
   branch names, commit messages, tests and documentation are written in English.
   The only Spanish in this repository lives inside `frontend/src/locales/es.json`
   — with one documented exception, the startup-failure dialog in
   `backend/app/desktop/__main__.py`, which fires before the web client exists
   and so cannot reach i18n. Do not add a second exception.
2. **Never write user-facing strings in components.** All UI copy goes through
   i18n keys (see `frontend/CLAUDE.md`).
3. **Respect the layers.** `router → service → repository → model` in the backend,
   `route → feature → api hook` in the frontend. Never skip a layer, never import
   backwards.
4. **The OpenAPI schema is the single source of truth for the API contract.**
   Frontend types are generated, never hand-written. Run `make gen-api` after any
   change to a route or response schema.
5. **Small, typed, boring code.** Prefer an obvious function over a clever one.
   No `any` in TypeScript, no untyped `def` in Python.
6. **Run `make check` before you report a task as done.** If it fails, fix it.
7. **Domain vocabulary is fixed.** Use the exact terms in `docs/domain-model.md`
   (`Teacher`, `ClassGroup`, `Subject`, `Room`, `TimeSlot`, `CurriculumEntry`,
   `Schedule`, `ScheduledSession`). Do not invent synonyms such as `Professor`,
   `Course`, `Slot` or `Lesson`.

## Layout

```
backend/    FastAPI + SQLAlchemy + OR-Tools application   → backend/CLAUDE.md
frontend/   Vite + React SPA                              → frontend/CLAUDE.md
packaging/  PyInstaller spec, Inno Setup script, icon     → packaging/README.md
docs/       Architecture, domain model, conventions, ADRs
```

Read the app-level `CLAUDE.md` of whichever side you are editing. It contains the
concrete file-by-file pattern to copy.

## Documentation map

| File | Read it when |
|---|---|
| `docs/domain-model.md` | You touch entities, database tables or business rules |
| `docs/architecture.md` | You add a module or wonder where code belongs |
| `docs/conventions.md`  | You need naming, error, logging or git conventions |
| `docs/vertical-slice.md` | You add a new feature end to end (**start here**) |
| `docs/adr/`            | You want to know why a decision was made, or make a new one |

## Commands

Everything is driven from the root `Makefile`:

```sh
make setup      # install backend + frontend dependencies and git hooks
make dev        # run API (:8000) and web (:5173) together
make check      # lint + type-check + tests for both sides — the gate
make gen-api    # regenerate the frontend API client from the backend OpenAPI
make migration name=add_something   # create an Alembic migration
make desktop    # run it the way the school does: one process, native window
```

## Definition of done

A change is finished when all of these hold:

- `make check` passes.
- New behaviour in the solver or in a service has a test in `backend/tests/`.
- New API surface is reflected in the generated frontend client (`make gen-api`).
- New user-facing text exists in `frontend/src/locales/es.json`.
- A schema change ships with an Alembic migration.
- A decision that constrains future work is recorded as an ADR in `docs/adr/`.

## It runs on a teacher's laptop, not on a server

Four consequences that catch people out:

- **There is no user, no role and no token.** Do not add an auth dependency to a
  route, a "current user" to a service, or an owner column to a table.
- **Never bind anything to `0.0.0.0`.** The loopback interface is the entire
  security model now that the login is gone. `docker-compose.yml` and the
  Dockerfiles were deleted for this reason; do not bring them back.
- **The user cannot read a stack trace, restart a service or open a terminal.**
  A failure has to end in something they can act on: a translated message, or
  the dialog that names the log file. "It does not open" is the report you will
  get otherwise.
- **The data outlives the program.** Schema changes ship with a migration
  because a school's database is upgraded in place, on their machine, with no
  one watching. Never write a migration that cannot run twice, and never make
  one that drops data the user still needs.

`app/desktop/` owns everything machine-specific. Services, repositories, models
and the solver must not import from it.

## This is a public, open-source project

The repository is MIT-licensed and public. Assume a stranger will read every
line you write:

- No secrets, no real school data, no personal data in code, fixtures or tests.
  Sample data uses `example.org` addresses.
- Public-facing documents (`README.md`, `CONTRIBUTING.md`, issue templates) are
  English; `README.es.md` is the Spanish translation and must be updated with it.
- Record user-visible changes under `## [Unreleased]` in `CHANGELOG.md`.
- Do not overstate what works. The status list in the README reflects reality.

## Scope discipline

Implement what was asked. If you spot an adjacent problem, write it down in the
response instead of fixing it silently. Do not add dependencies, background jobs,
caching layers or abstractions that no current feature needs.
