import type { Conflict, ScheduledSession, TimeSlot } from "@/features/schedules/api";
import { toApiError } from "@/lib/api/client";
import { getErrorMessageKeys } from "@/lib/api/error-translation";
import { formatTime } from "@/lib/time-format";
import { weekdayTranslationKey } from "@/lib/weekdays";

/** `day_of_week` is 0 = Monday … 4 = Friday; the school week has no weekend. */
export interface ScheduleDay {
  dayOfWeek: number;
  slots: TimeSlot[];
}

/**
 * A grid cell is addressed by (time slot, class group), never by session id:
 * a solver run rewrites every unlocked session and their ids churn (ADR 0004).
 */
export function cellKey(timeSlotId: number, classGroupId: number): string {
  return `${String(timeSlotId)}:${String(classGroupId)}`;
}

export function indexSessionsByCell(
  sessions: readonly ScheduledSession[],
): Map<string, ScheduledSession> {
  const index = new Map<string, ScheduledSession>();
  for (const session of sessions) {
    index.set(cellKey(session.time_slot_id, session.class_group_id), session);
  }
  return index;
}

/** Slots ordered into the rows of the week, grouped under their weekday. */
export function groupSlotsByDay(slots: readonly TimeSlot[]): ScheduleDay[] {
  const days = new Map<number, TimeSlot[]>();
  for (const slot of slots) {
    const existing = days.get(slot.day_of_week);
    if (existing === undefined) {
      days.set(slot.day_of_week, [slot]);
    } else {
      existing.push(slot);
    }
  }

  return [...days.entries()]
    .map(([dayOfWeek, daySlots]) => ({
      dayOfWeek,
      slots: [...daySlots].sort((left, right) => left.period_index - right.period_index),
    }))
    .sort((left, right) => left.dayOfWeek - right.dayOfWeek);
}

/** i18n key for a weekday, or `undefined` for a day outside the school week. */
/** Conflicts have no id of their own; this one is stable across a refetch. */
export function conflictId(conflict: Conflict): string {
  return `${conflict.code}:${conflict.entry_ids.join(",")}:${String(conflict.slot_id ?? "")}`;
}

/**
 * Cells a conflict points at. A conflict names curriculum entries and, for
 * everything but `curriculum_not_covered`, the slot they collide in.
 */
export function conflictCellKeys(
  conflict: Conflict,
  sessions: readonly ScheduledSession[],
): Set<string> {
  const entryIds = new Set(conflict.entry_ids);
  const keys = new Set<string>();

  for (const session of sessions) {
    if (!entryIds.has(session.curriculum_entry_id)) {
      continue;
    }
    if (conflict.slot_id !== null && conflict.slot_id !== undefined) {
      if (session.time_slot_id !== conflict.slot_id) {
        continue;
      }
    }
    keys.add(cellKey(session.time_slot_id, session.class_group_id));
  }

  return keys;
}

/**
 * Translation keys for a refused edit, most specific first. A broken constraint
 * arrives as the generic `conflict` code, which in this screen means something
 * far more precise than it does on a delete, so a schedule-specific key is
 * tried before the shared one and i18next falls back for every other code.
 */
export function getSessionEditErrorKeys(error: unknown): string[] {
  const { code } = toApiError(error);
  return [`schedules.editErrors.${code}`, ...getErrorMessageKeys(error)];
}

// Weekday and time formatting are shared with the availability and print
// screens; this module only re-exports them so grid components have one import.
export { formatTime, weekdayTranslationKey as weekdayKey };
