import type { ScheduledSession, TimeSlot } from "@/features/schedule-print/api";

/** The three ways a finished timetable can be sliced for printing. */
export type ViewType = "teacher" | "classGroup" | "room";

export const VIEW_TYPES: readonly ViewType[] = ["teacher", "classGroup", "room"];

/** One weekday column. `dayOfWeek` follows the domain model: 0 = Monday. */
export const WEEKDAYS = [
  { dayOfWeek: 0, key: "monday" },
  { dayOfWeek: 1, key: "tuesday" },
  { dayOfWeek: 2, key: "wednesday" },
  { dayOfWeek: 3, key: "thursday" },
  { dayOfWeek: 4, key: "friday" },
] as const;

/** One selectable teacher, class group or room, derived from session rows. */
export interface ViewEntity {
  id: number;
  name: string;
}

/** One filled or empty cell of the printed week. */
export interface WeekGridCell {
  /** Ordered lines of text, e.g. group, subject and room for a teacher's sheet. */
  lines: string[];
}

/** One row of the printed week, spanning every weekday column. */
export interface WeekGridRow {
  periodIndex: number;
  startTime: string;
  endTime: string;
  isBreak: boolean;
  cellsByDay: (WeekGridCell | undefined)[];
}

function entityIdOf(session: ScheduledSession, viewType: ViewType): number | null {
  if (viewType === "teacher") return session.teacher_id;
  if (viewType === "classGroup") return session.class_group_id;
  return session.room_id ?? null;
}

function entityNameOf(session: ScheduledSession, viewType: ViewType): string | null {
  if (viewType === "teacher") return session.teacher_name;
  if (viewType === "classGroup") return session.class_group_name;
  return session.room_name ?? null;
}

/**
 * Every distinct teacher, class group or room that appears in the schedule's
 * sessions, sorted by name. A room-less session (no room assigned) is not a
 * selectable "room" entity.
 */
export function getViewEntities(sessions: ScheduledSession[], viewType: ViewType): ViewEntity[] {
  const byId = new Map<number, string>();
  for (const session of sessions) {
    const id = entityIdOf(session, viewType);
    const name = entityNameOf(session, viewType);
    if (id !== null && name !== null) {
      byId.set(id, name);
    }
  }
  return Array.from(byId, ([id, name]) => ({ id, name })).sort((a, b) =>
    a.name.localeCompare(b.name, "es"),
  );
}

/** The ordered lines shown in one cell, per ADR 0004's field naming. */
function cellLinesFor(session: ScheduledSession, viewType: ViewType): string[] {
  if (viewType === "teacher") {
    return [session.class_group_name, session.subject_name, session.room_name ?? ""];
  }
  if (viewType === "classGroup") {
    return [session.subject_name, session.teacher_name, session.room_name ?? ""];
  }
  return [session.class_group_name, session.subject_name, session.teacher_name];
}

/**
 * Builds one printable week for a single teacher, class group or room: every
 * distinct period of the day as a row (breaks included), every weekday as a
 * column, with at most one session per cell -- the schedule's no-overlap
 * invariants guarantee that for a single entity.
 */
export function buildWeekGrid(
  timeSlots: TimeSlot[],
  sessions: ScheduledSession[],
  viewType: ViewType,
  entityId: number,
): WeekGridRow[] {
  const periodIndexes = Array.from(new Set(timeSlots.map((slot) => slot.period_index))).sort(
    (a, b) => a - b,
  );
  const entitySessions = sessions.filter((session) => entityIdOf(session, viewType) === entityId);

  return periodIndexes.map((periodIndex) => {
    const slotsAtPeriod = timeSlots.filter((slot) => slot.period_index === periodIndex);
    const representative = slotsAtPeriod.find((slot) => slot.day_of_week === 0) ?? slotsAtPeriod[0];

    const cellsByDay = WEEKDAYS.map(({ dayOfWeek }) => {
      const session = entitySessions.find(
        (candidate) =>
          candidate.day_of_week === dayOfWeek && candidate.period_index === periodIndex,
      );
      return session ? { lines: cellLinesFor(session, viewType) } : undefined;
    });

    return {
      periodIndex,
      startTime: representative?.start_time ?? "",
      endTime: representative?.end_time ?? "",
      isBreak: representative?.is_break ?? false,
      cellsByDay,
    };
  });
}

export { formatTime } from "@/lib/time-format";
