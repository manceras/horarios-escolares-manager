# 4. Shape of the schedule API and how a run replaces sessions

- Status: accepted
- Date: 2026-09-04

## Context

ADR 0003 chose CP-SAT and isolated it behind a pure `TimetableSolver`. That left
three questions open once the solver was wired to the database, all of which
constrain code written later:

1. What a schedule looks like over HTTP, given that the main consumer is a dense
   weekly grid that renders one cell per (day, period, group).
2. What a second solver run does to the sessions a first run produced, and what
   happens to the ones a human pinned.
3. How a manual drag-and-drop edit is validated, when a draft timetable is
   routinely incomplete and therefore already "invalid".

## Decision

### The grid reads denormalised session rows

`GET /api/v1/schedules/{id}` returns the schedule plus a flat `sessions` array.
Each session already carries every label the grid paints — `class_group_name`,
`subject_code`, `subject_name`, `teacher_name`, `room_name`, `day_of_week`,
`period_index`, `start_time`, `end_time` — next to the ids behind them. The list
is ordered by day, then period, then group name.

The frontend therefore renders a week from one request, with no client-side join
against `/teachers`, `/rooms` or `/time-slots`, and no N+1 of its own. The cost is
duplicated labels on the wire and a response that must be rebuilt when a name
changes; for a school-sized timetable (a few hundred sessions) that is cheap, and
it keeps the grid component free of lookup tables.

Listing endpoints return `ScheduleRead`, the same object without `sessions`.

### A run rewrites the unlocked timetable and preserves pins by identity

`POST /{id}/generate` feeds every `locked` session back to the solver as a fixed
assignment, then, on success:

- deletes the schedule's unlocked sessions and inserts the solver's assignments
  as new rows;
- keeps each locked row, with its own id, rather than deleting and recreating it,
  so a pin the user set survives as the same resource;
- fills in the room of a locked session that had none, using the room the solver
  chose for it.

An infeasible run writes no session at all. It records `solver_status` and
returns HTTP 200 with `solved: false` and the solver's message: impossible
constraints are the user's answer, not a server error. The previously stored
timetable is left untouched.

Generation is synchronous, bounded by `settings.solver_time_limit_seconds`, as
ADR 0003 decided. Only a `draft` may be generated, edited or published; a
`published` schedule is archived, never edited.

### A manual edit is rejected only for the conflicts it introduces

`PATCH /{id}/sessions/{session_id}` applies the move to a copy of the timetable
and runs `find_conflicts` from `app/solver/validation.py` — the same check the
tests use — before and after. The edit is rejected with `ConflictError`, naming
the violated constraint code, only when a conflict appears that was not there
before.

The diff matters because `find_conflicts` also reports `curriculum_not_covered`,
which is true of every half-built draft and has nothing to do with the move.
Comparing before and after lets one validator serve both the strict check
(`GET /{id}/conflicts` reports everything) and the permissive one (an edit is
judged only on what it breaks), instead of splitting the hard constraints into
two lists that would drift apart.

## Consequences

- Adding a hard constraint to `validation.py` automatically tightens manual edits.
  Nothing in the service enumerates constraints, so nothing there has to change.
- The session response is the grid's contract. Adding a displayed field means
  extending `ScheduledSessionRead` and running `make gen-api`.
- Regeneration is destructive for unlocked sessions: any per-session state added
  later (a note, a substitution) must either live on a locked session or be keyed
  by curriculum entry rather than by session id.
- Because assignments are rewritten rather than diffed, session ids churn on every
  run. The frontend must key grid cells by (`time_slot_id`, `class_group_id`), not
  by session id, outside of an edit round trip.
- `ScheduleRepository` reads slots, rooms, teachers, curriculum and
  unavailabilities as well as its own aggregate. That is deliberate: they are the
  inputs of a generation run and are loaded eagerly in one place. If those
  entities grow their own repositories, the solver-input queries move there.
