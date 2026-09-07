# Contributing

Thanks for considering a contribution. This project is built for real schools,
so bug reports from people who actually make timetables are as valuable as code.

## Before you start

- Open an issue first for anything larger than a bug fix, so we agree on the
  approach before you spend time on it.
- Read [`CLAUDE.md`](CLAUDE.md). It is the project's contract: layers, naming,
  error handling and the definition of done. It applies to everyone, whether you
  write the code yourself or with an AI assistant.
- Read [`docs/vertical-slice.md`](docs/vertical-slice.md) — a step-by-step recipe
  for adding a feature end to end.

## Setup

```sh
make setup      # installs backend, frontend and the git hooks
make check      # must pass before you push
```

## Ground rules

1. **English in the repository.** Code, comments, docs and commit messages are
   English. User-facing text is Spanish and lives only in
   `frontend/src/locales/es.json`.
2. **Respect the layers.** `router → service → repository → model` on the
   backend, `route → feature → api hook` on the frontend. The solver never
   touches the database.
3. **Types are not optional.** `mypy --strict` and TypeScript `strict` both pass.
4. **Test what matters.** Solver constraints, service invariants and bug fixes
   need a test. UI tests are welcome but not required.
5. **The API contract is generated.** After changing a route or a schema, run
   `make gen-api` and commit nothing from `schema.d.ts` (it is git-ignored).

## Commits and pull requests

[Conventional Commits](https://www.conventionalcommits.org/), in English:

```
feat(solver): add teacher availability constraint
fix(api): return 409 when a group already has that subject
```

Scopes: `api`, `solver`, `db`, `desktop`, `web`, `ui`, `deps`, `ci`, `docs`.

A pull request should do one thing, explain why, and leave `make check` green.
If it changes behaviour a school would notice, say so in the description.

## Adding a constraint to the solver

This is the most common meaningful contribution. Do all four:

1. Describe it in `docs/domain-model.md`, marked as hard or soft.
2. Implement it in `backend/app/solver/cpsat.py`.
3. Check it in `backend/app/solver/validation.py` so manual edits are caught too.
4. Test it in `backend/tests/test_solver.py`.

## Reporting a bug

Include the school shape that triggers it (how many groups, teachers, periods),
what you expected and what happened. If the solver returned an impossible or
infeasible timetable, the curriculum data that caused it is the most useful
thing you can attach.
