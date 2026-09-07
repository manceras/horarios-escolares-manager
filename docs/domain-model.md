# Domain model

The vocabulary below is canonical. Code, database tables, API paths and
documentation use exactly these names in English; the Spanish term is only a
translation hint for the UI copy.

| Entity | Spanish | Meaning |
|---|---|---|
| `Teacher` | profesor/a | A member of the teaching staff. |
| `Subject` | asignatura | A curricular subject (Maths, Music, PE...). |
| `ClassGroup` | grupo / clase | A group of pupils that stays together, e.g. `3ºA`. |
| `Room` | aula / espacio | A physical space. Some are shared resources (gym, music room). |
| `TimeSlot` | franja horaria | A weekday + period, e.g. Monday 09:00–09:45. |
| `CurriculumEntry` | carga lectiva | "Group X studies Subject Y with Teacher Z for N periods a week". |
| `Schedule` | horario | One complete timetable version for the school. |
| `ScheduledSession` | sesión | One curriculum entry placed in a time slot and a room. |
| `TeacherUnavailability` | indisponibilidad | A slot in which a teacher cannot teach. |
| `User` | usuario | Someone who logs in. Optionally linked to a `Teacher`. |

## Entities

### Teacher
`id`, `first_name`, `last_name`, `email` (unique), `is_specialist`,
`max_periods_per_week`, `active`.

A **specialist** (English, PE, Music, Religion) rotates across groups instead of
staying with one group. A non-specialist is usually the tutor of one group.

### Subject
`id`, `code` (unique, e.g. `MAT`), `name`, `required_room_type` (nullable).

If `required_room_type` is set, sessions of this subject may only be placed in a
room of that type.

### ClassGroup
`id`, `name` (unique, e.g. `3A`), `grade` (1–6), `tutor_id` (nullable `Teacher`),
`home_room_id` (nullable `Room`).

### Room
`id`, `name` (unique), `room_type` (`classroom` | `gym` | `music` | `computer_lab`
| `other`), `capacity`.

A room hosts at most one session per time slot.

### TimeSlot
`id`, `day_of_week` (0 = Monday … 4 = Friday), `period_index` (0-based order
within the day), `start_time`, `end_time`, `is_break`.

Break slots (recreo) are never used for teaching. `(day_of_week, period_index)` is
unique.

### TeacherUnavailability
`id`, `teacher_id`, `time_slot_id`, `reason` (nullable).
Unique per `(teacher_id, time_slot_id)`. Absence of a row means available.

### CurriculumEntry
`id`, `class_group_id`, `subject_id`, `teacher_id`, `periods_per_week`.
Unique per `(class_group_id, subject_id)`. This is the solver's input: what has to
be placed, how often and by whom.

### Schedule
`id`, `name`, `status` (`draft` | `published` | `archived`), `created_at`,
`generated_at` (nullable), `solver_status` (nullable).

At most one schedule is `published` at a time.

### ScheduledSession
`id`, `schedule_id`, `curriculum_entry_id`, `time_slot_id`, `room_id` (nullable),
`locked`.

A `locked` session is pinned by a human and must be preserved by any later solver
run.

## Invariants

These are enforced in services and re-checked by the solver. Every one of them has
a test in `backend/tests/`.

1. **No teacher overlap** — a teacher has at most one session per time slot.
2. **No group overlap** — a class group has at most one session per time slot.
3. **No room overlap** — a room hosts at most one session per time slot.
4. **Teacher availability** — no session in a slot where the teacher is unavailable.
5. **Room type** — a subject with `required_room_type` is placed in a matching room.
6. **Curriculum coverage** — a schedule places exactly `periods_per_week` sessions
   for every curriculum entry.
7. **No teaching in breaks** — no session lands on a slot with `is_break = true`.
8. **Teacher load** — sessions per teacher per week ≤ `max_periods_per_week`.
9. **One subject per group per day** — at most one session of the same subject for
   the same group on the same day (soft constraint; may be relaxed by the solver).

Constraints 1–8 are **hard**: a schedule violating them is invalid. Constraint 9
and any future pedagogical preference are **soft**: the solver minimises their
violations but a solution may break them.

## Users and roles

There are none. The application runs on one person's computer with no login;
see [ADR 0006](adr/0006-desktop-application.md). A `User` table, roles and
per-teacher permissions existed until that decision and were removed rather
than left disabled.
