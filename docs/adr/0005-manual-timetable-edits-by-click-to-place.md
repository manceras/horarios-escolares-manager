# 5. Manual timetable edits are click-to-place, not drag-and-drop

- Status: accepted
- Date: 2026-09-04

## Context

ADR 0004 gave the weekly grid a `PATCH` that moves one session to another time
slot and validates the whole timetable before accepting it. The screen still had
to choose how a human expresses that move.

Drag-and-drop is the obvious gesture for a timetable, but it is the expensive
one. The HTML5 drag API is not operable from the keyboard and is unreliable on
touch, so an accessible implementation means a library (`dnd-kit` is the
maintained, accessible option) plus its keyboard sensor, live-region
announcements and sortable/droppable wiring — a new runtime dependency and a
second interaction model to keep correct, for one screen.

## Decision

A move is two clicks. The user presses **Mover** on a session, the grid marks
the cells that can receive it, and pressing one of them sends the `PATCH`.
Pressing **Cancelar** on the selected session, or moving it, ends the gesture.

Both steps are ordinary `<button>` elements inside the table cells, so the whole
interaction is reachable by Tab, activates with Enter or Space, and exposes its
state through `aria-pressed`. No drag-and-drop dependency is added.

The grid only offers the cells that could plausibly accept the session: free,
non-break cells in the same class group column, because a session belongs to a
curriculum entry, which fixes its class group, and a group holds at most one
session per slot. Everything beyond that — a teacher already busy, a room clash,
a teacher's unavailability — is the server's decision, not the grid's; the grid
never re-implements a constraint that `validation.py` already owns.

The move is applied optimistically to the cached schedule and rolled back to the
snapshot taken before the request when the server answers 409, so a refused move
never stays on screen.

## Consequences

- The frontend keeps its dependency list unchanged, and the edit interaction is
  keyboard- and screen-reader-operable without any extra machinery.
- The gesture costs one more click than dragging, and it is less discoverable.
  If teachers report that in use, dragging can be added later as a second path
  to the same `onMoveSession` callback — the grid already routes every edit
  through one function — and the click path stays as the accessible fallback.
  Adding it would mean a new ADR and a real dependency, not an ad-hoc listener.
- Because valid targets are computed from the class group column alone, a future
  feature that lets a session change group (a split or a swap) has to extend
  `ScheduleGrid.isMoveTarget` as well as the API.
