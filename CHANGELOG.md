# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Domain model, migrations and development seed data for a primary school.
- OR-Tools CP-SAT timetable solver behind a `TimetableSolver` protocol, with
  teacher, group and room conflict constraints, availability, room types,
  weekly load, break slots and locked sessions.
- `find_conflicts()`, an independent validator for manually edited timetables.
- JWT authentication with `admin`, `head_of_studies` and `teacher` roles.
- Teachers REST endpoints and web page, as the reference vertical slice.
- Generated frontend API client derived from the backend OpenAPI document.
- Docker Compose deployment, pre-commit hooks and GitHub Actions CI.
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
- Curriculum screen: assign a subject and teacher to a class group with a
  weekly period count, grouped by class group with a subtotal, plus the
  workload report (assigned vs. available periods per group, assigned vs.
  maximum per teacher) so a head of studies sees whether a timetable is
  possible before generating one.

### Fixed

- The solver no longer discards a locked session it cannot place. When school
  data changes under a pin — the slot becomes a break, the room stops matching
  the subject — it reports `infeasible` and names the entry instead of returning
  an "optimal" timetable that contradicts the lock.
- Solver runs are reproducible: the same input now always produces the same
  timetable.
