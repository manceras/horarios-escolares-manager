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
