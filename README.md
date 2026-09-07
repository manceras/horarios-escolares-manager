# horarios-escolares-manager

Open-source timetable planner for primary schools. **A desktop program you
install and double-click** — no server, no accounts, no password. Windows
installer and Linux AppImage.

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
- [x] Windows installer and Linux AppImage, automatic backups, in-app updates
- [x] REST API for teachers, groups, subjects, rooms, time slots, availability
      and curriculum entries, with the business rules enforced in services
- [x] Endpoints to run the solver, persist a schedule, publish it, and validate
      manual edits against the hard constraints
- [x] Workload report that flags an impossible timetable before solving
- [x] Web UI for teachers, with the shared table, dialog and form building blocks
      every other screen will reuse
- [x] Web UI for every entity: teachers, availability, groups, subjects, rooms,
      time slots and the curriculum, with a workload report
- [x] Weekly grid UI: run the solver, see conflicts, move and lock sessions with
      the server validating every edit, publish a schedule
- [x] Printable views and CSV export per teacher, group and room
- [ ] A signed installer (unsigned today, so Windows shows a SmartScreen warning)
- [ ] More than one school year at a time
- [ ] macOS build
- [ ] In-app updates on Linux (Windows only today)

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
| Desktop | pywebview (Edge WebView2), PyInstaller, Inno Setup, AppImage |

The frontend API client is generated from the backend's OpenAPI document, so the
contract cannot drift unnoticed.

## Installing it (for a school)

### Windows

Download `Horarios-Setup-x.y.z.exe` from the
[latest release](https://github.com/manceras/horarios-escolares-manager/releases/latest)
and run it. It installs for the current user, so it never asks for an
administrator password, and it puts *Horarios* on the desktop and in the Start
menu.

The installer is not code-signed yet, so the first run shows **"Windows
protected your PC"**. Click *More info*, then *Run anyway*. Verify the download
against the `.sha256` published beside it if you want to be sure of it first.

The program updates itself: when a new version exists it offers it in a strip
across the top of the window, and one click installs it.

### Linux

Download `Horarios-x.y.z-x86_64.AppImage`, make it executable and run it:

```sh
chmod +x Horarios-*.AppImage
./Horarios-*.AppImage
```

No package manager, no root, no install. It opens in a chromeless Chromium
window where one is available, and in your default browser otherwise — see
[`packaging/README.md`](packaging/README.md) for why there is no native window.
Linux builds do not update themselves; the banner points at the releases page.

### Where the data lives

Everything is in one folder — `%LOCALAPPDATA%\Horarios\` on Windows,
`~/.local/share/horarios/` on Linux:

```
horarios.db      the school's data
backups/         a copy from each of the last ten times it was opened
horarios.log     what to send if something goes wrong
```

Copying that folder is a complete backup and a complete move to another
computer. Uninstalling the program leaves it alone.

## Running from source

Requirements: Python 3.12+ with [uv](https://docs.astral.sh/uv/) and Node 22+
with pnpm.

```sh
git clone https://github.com/manceras/horarios-escolares-manager.git
cd horarios-escolares-manager
make setup
make migrate
make seed          # sample school: 6 groups, 9 teachers, 54 curriculum entries
make dev           # API on :8000, web on :5173
```

Interactive API docs: <http://localhost:8000/docs>.

`make desktop` runs the packaged shell — one process, native window, the real
data directory — without building an installer.

## Building the installer

The Windows installer is built by GitHub Actions on a tag, because PyInstaller
cannot cross-compile:

```sh
# bump app.__version__ in backend/app/__init__.py first; CI checks it matches
git tag v0.2.0 && git push origin v0.2.0
```

The workflow builds both the Windows installer and the Linux AppImage, publishes
a SHA-256 next to each and attaches them all to the release. `make appimage`
builds the Linux one locally; see [`packaging/`](packaging/) for the rest.

## Everyday commands

```sh
make check      # lint, types and tests for both sides. Run before every commit
make fix        # auto-fix formatting and lint
make gen-api    # regenerate the frontend client after an API change
make migration name=add_rooms
make desktop    # run the packaged desktop shell from source
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
