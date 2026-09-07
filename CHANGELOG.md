# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing yet.

## [0.1.0] - 2026-09-07

First release: a Windows installer and a Linux AppImage.

### Changed

- **The application is now a Windows desktop program, not a server.** It runs on
  the planner's own machine as a single process bound to `127.0.0.1`, serving
  the web client itself in a native window.

### Removed

- **Authentication.** There is no login, no user account and no role: the
  machine's own account is the boundary. See
  [ADR 0006](docs/adr/0006-desktop-application.md).
- **`docker-compose.yml` and both Dockerfiles**, so that an application without
  authentication cannot be exposed to a network in one command.

### Added

- Domain model, migrations and development seed data for a primary school.
- OR-Tools CP-SAT timetable solver behind a `TimetableSolver` protocol, with
  teacher, group and room conflict constraints, availability, room types,
  weekly load, break slots and locked sessions.
- `find_conflicts()`, an independent validator for manually edited timetables.
- A Windows installer and a Linux AppImage, built by CI on a tag and published
  with a SHA-256 each.
- Automatic rotating backups of the database, taken on every start, and schema
  migrations applied automatically so an update needs no intervention.
- In-app update checking and one-click installation, with the download verified
  against its published checksum before it is run.
- Teachers REST endpoints and web page, as the reference vertical slice.
- Generated frontend API client derived from the backend OpenAPI document.
- Pre-commit hooks and GitHub Actions CI.
- CRUD endpoints for rooms, subjects, class groups, time slots, teacher
  unavailability and curriculum entries, each with its business rules enforced
  in the service layer.
- Bulk replacement of a teacher's weekly availability in one transaction.
- `GET /api/v1/curriculum-entries/workload`, a feasibility report telling a head
  of studies that a timetable is impossible before the solver is run.
- Timetable generation endpoints: create a draft, run the solver, inspect
  conflicts, move or lock a session, publish and archive.
- Shared frontend building blocks for data-entry screens: `DataTable`,
  `EntityDialog`, `ConfirmDialog`, a typed form helper and app-level toasts that
  translate backend error codes.
- Teachers screen completed with create, edit and delete.
- Rooms and subjects screens, with room type shown as a translated label and a
  subject's required room type selectable (including "no special room
  required").
- Curriculum screen: assign a subject and teacher to a class group with a
  weekly period count, grouped by class group with a subtotal, plus the
  workload report (assigned vs. available periods per group, assigned vs.
  maximum per teacher) so a head of studies sees whether a timetable is
  possible before generating one.

### Added

- `make create-user`, a command-line way to create an account. It prompts for the
  password, so a real deployment no longer depends on the development seed and
  its public password to get its first administrator in.

### Changed

- Development seed data now describes a full six-grade school: six groups with
  their tutors, three rotating specialists, nine subjects with their statutory
  weekly load, special rooms, and a part-time teacher who is unavailable two days
  a week. The previous single-group sample could not exercise the solver.
- Schedules screens: a list to create, publish and delete timetable versions,
  and a weekly grid — time slots down the side, one column per class group,
  breaks marked and never editable — with solver generation, its outcome and
  infeasibility message, a translated conflict list that highlights the cell it
  refers to, session locking, and manual moves by click-to-place that are undone
  on screen when the server refuses them.

### Fixed

- Deleting a teacher who still taught something left orphaned curriculum entries
  behind and made the curriculum endpoints fail with a 500. Teacher deletion now
  refuses with a 409 naming what still references them.
- SQLite now enforces foreign keys. Until this release the schema's `ForeignKey`
  and `ON DELETE CASCADE` clauses did nothing at runtime, so any unguarded delete
  could leave dangling references. A constraint the database refuses is reported
  as a 409 instead of surfacing as a server error.

- The solver no longer discards a locked session it cannot place. When school
  data changes under a pin — the slot becomes a break, the room stops matching
  the subject — it reports `infeasible` and names the entry instead of returning
  an "optimal" timetable that contradicts the lock.
- Solver runs are reproducible: the same input now always produces the same
  timetable.
