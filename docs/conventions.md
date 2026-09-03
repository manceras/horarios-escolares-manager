# Conventions

## Language

English for everything committed to the repository. Spanish appears only as
translation values in `frontend/src/locales/es.json`.

## Naming

| Thing | Convention | Example |
|---|---|---|
| Python module | `snake_case`, singular | `app/services/teacher_service.py` |
| Python class | `PascalCase` | `TeacherService` |
| SQLAlchemy table | `snake_case`, plural | `class_groups` |
| API path | kebab/plural nouns | `/api/v1/class-groups/{id}` |
| Pydantic schema | `<Entity><Purpose>` | `TeacherCreate`, `TeacherRead` |
| React component file | `PascalCase.tsx` | `TeacherTable.tsx` |
| React hook | `use<Thing>` | `useTeachers` |
| i18n key | `<area>.<element>` | `teachers.createButton` |
| Test | `test_<behaviour>` | `test_rejects_overlapping_session` |

Booleans read as assertions: `is_specialist`, `has_conflicts`, `locked`.
Avoid abbreviations; `curriculum_entry`, never `ce` or `entry`.

## Python

- Type every signature. `mypy --strict` must pass; no `# type: ignore` without a
  comment explaining why.
- SQLAlchemy 2.0 style: `Mapped[...]` / `mapped_column(...)`, `select()` queries.
- Pydantic v2. Validation lives in schemas, not in routers.
- No business logic in routers; a router is routing, auth and delegation.
- Comments explain *why*. If a comment explains *what*, rename things instead.

## TypeScript

- `strict` plus `noUncheckedIndexedAccess`. No `any`, no non-null `!` assertions;
  narrow properly.
- Function components, named exports, one component per file.
- Data fetching only through TanStack Query hooks in `src/features/*/api.ts`.
- Query keys come from `src/lib/api/query-keys.ts` — never inline an array.
- Tailwind utilities in the markup; use `cn()` to merge conditional classes.

## Errors and messages

Backend error messages are English, factual and safe to log. The frontend maps an
error `code` to a Spanish message through i18n; it never shows a raw backend
string to the user.

## Git

Conventional Commits, imperative mood, English:

```
feat(solver): add teacher availability constraint
fix(api): return 409 when a group already has that subject
chore(deps): bump vite to 7.1
docs(adr): record the choice of CP-SAT
```

Scopes: `api`, `solver`, `db`, `auth`, `web`, `ui`, `deps`, `ci`, `docs`.
Branches: `feat/teacher-availability`, `fix/room-overlap`.
One logical change per commit. Never commit generated files or `*.db`.

## Testing

Tests are optional for UI work and **required** for:

- solver behaviour and every hard constraint,
- service-level invariants,
- bug fixes (a failing test first, then the fix).

`backend/tests/` mirrors `app/`. Use the `client` and `session` fixtures from
`conftest.py`; each test gets a fresh in-memory database.
