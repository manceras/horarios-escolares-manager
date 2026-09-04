import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import type { ClassGroup, ScheduledSession, TimeSlot } from "@/features/schedules/api";
import { ScheduleGridRow } from "@/features/schedules/ScheduleGridRow";
import {
  cellKey,
  groupSlotsByDay,
  indexSessionsByCell,
  weekdayKey,
} from "@/features/schedules/schedule-grid";

export interface ScheduleGridProps {
  sessions: readonly ScheduledSession[];
  timeSlots: readonly TimeSlot[];
  classGroups: readonly ClassGroup[];
  /** A published schedule is read-only: no move, no lock. */
  isEditable: boolean;
  isBusy: boolean;
  highlightedCellKeys: ReadonlySet<string>;
  onMoveSession: (session: ScheduledSession, targetTimeSlot: TimeSlot) => void;
  onToggleLock: (session: ScheduledSession) => void;
}

/**
 * The week as a table: one row per time slot, one column per class group.
 *
 * Cells are keyed by (time slot, class group) because a solver run rewrites
 * every unlocked session and their ids churn (ADR 0004). Moving is a two-step
 * click -- select a session, then pick a free cell in the same column -- so the
 * whole interaction works from the keyboard and with a screen reader.
 */
export function ScheduleGrid({
  sessions,
  timeSlots,
  classGroups,
  isEditable,
  isBusy,
  highlightedCellKeys,
  onMoveSession,
  onToggleLock,
}: ScheduleGridProps) {
  const { t } = useTranslation();
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const days = useMemo(() => groupSlotsByDay(timeSlots), [timeSlots]);
  const sessionsByCell = useMemo(() => indexSessionsByCell(sessions), [sessions]);
  const selectedSession = sessions.find((session) => session.id === selectedSessionId);

  useEffect(() => {
    const [firstKey] = [...highlightedCellKeys];
    if (firstKey === undefined) {
      return;
    }
    scrollRef.current
      ?.querySelector(`[data-cell-key="${firstKey}"]`)
      ?.scrollIntoView({ block: "center", inline: "center" });
  }, [highlightedCellKeys]);

  if (days.length === 0 || classGroups.length === 0) {
    return <p className="text-sm text-muted-foreground">{t("schedules.gridEmpty")}</p>;
  }

  /**
   * A session belongs to a curriculum entry, which fixes its class group, and a
   * group holds at most one session per slot -- so the only cells worth
   * offering are the free teaching cells of the same column.
   */
  function isMoveTarget(slot: TimeSlot, group: ClassGroup): boolean {
    if (selectedSession === undefined || slot.is_break) {
      return false;
    }
    return (
      selectedSession.class_group_id === group.id &&
      sessionsByCell.get(cellKey(slot.id, group.id)) === undefined
    );
  }

  function handleSelectSession(session: ScheduledSession): void {
    setSelectedSessionId((current) => (current === session.id ? null : session.id));
  }

  function handlePlaceInSlot(slot: TimeSlot): void {
    if (selectedSession !== undefined) {
      onMoveSession(selectedSession, slot);
    }
    setSelectedSessionId(null);
  }

  return (
    <div ref={scrollRef} className="overflow-x-auto rounded-md border border-border">
      <table className="w-full min-w-[48rem] border-collapse text-sm">
        <caption className="sr-only">{t("schedules.gridCaption")}</caption>
        <thead>
          <tr>
            <th
              scope="col"
              className="sticky left-0 z-10 w-32 border border-border bg-background p-2 text-left font-medium"
            >
              {t("schedules.slotColumn")}
            </th>
            {classGroups.map((group) => (
              <th
                key={group.id}
                scope="col"
                className="border border-border bg-background p-2 text-left font-medium"
              >
                {group.name}
              </th>
            ))}
          </tr>
        </thead>
        {days.map((day) => {
          const dayKey = weekdayKey(day.dayOfWeek);
          return (
            <tbody key={day.dayOfWeek}>
              <tr>
                <th
                  scope="colgroup"
                  colSpan={classGroups.length + 1}
                  className="border border-border bg-muted p-2 text-left font-semibold"
                >
                  {dayKey === undefined ? t("schedules.unknownWeekday") : t(dayKey)}
                </th>
              </tr>
              {day.slots.map((slot) => (
                <ScheduleGridRow
                  key={slot.id}
                  slot={slot}
                  classGroups={classGroups}
                  sessionsByCell={sessionsByCell}
                  isEditable={isEditable}
                  isBusy={isBusy}
                  selectedSessionId={selectedSessionId}
                  highlightedCellKeys={highlightedCellKeys}
                  isMoveTarget={isMoveTarget}
                  onSelectSession={handleSelectSession}
                  onPlaceInSlot={handlePlaceInSlot}
                  onToggleLock={onToggleLock}
                />
              ))}
            </tbody>
          );
        })}
      </table>
    </div>
  );
}
