import { useTranslation } from "react-i18next";

import type { ClassGroup, ScheduledSession, TimeSlot } from "@/features/schedules/api";
import { ScheduleGridCell } from "@/features/schedules/ScheduleGridCell";
import { cellKey, formatTime } from "@/features/schedules/schedule-grid";

export interface ScheduleGridRowProps {
  slot: TimeSlot;
  classGroups: readonly ClassGroup[];
  sessionsByCell: ReadonlyMap<string, ScheduledSession>;
  isEditable: boolean;
  isBusy: boolean;
  selectedSessionId: number | null;
  highlightedCellKeys: ReadonlySet<string>;
  /** Decided by the grid, which knows which session is selected. */
  isMoveTarget: (slot: TimeSlot, group: ClassGroup) => boolean;
  onSelectSession: (session: ScheduledSession) => void;
  onPlaceInSlot: (slot: TimeSlot) => void;
  onToggleLock: (session: ScheduledSession) => void;
}

/** One time slot of the week: its label, then one cell per class group. */
export function ScheduleGridRow({
  slot,
  classGroups,
  sessionsByCell,
  isEditable,
  isBusy,
  selectedSessionId,
  highlightedCellKeys,
  isMoveTarget,
  onSelectSession,
  onPlaceInSlot,
  onToggleLock,
}: ScheduleGridRowProps) {
  const { t } = useTranslation();
  const slotLabel = `${formatTime(slot.start_time)}–${formatTime(slot.end_time)}`;

  return (
    <tr>
      <th
        scope="row"
        className="sticky left-0 z-10 border border-border bg-background p-2 text-left font-normal whitespace-nowrap"
      >
        <span className="block">{slotLabel}</span>
        {slot.is_break ? (
          <span className="block text-xs text-muted-foreground">{t("schedules.breakSlot")}</span>
        ) : null}
      </th>
      {classGroups.map((group) => {
        const key = cellKey(slot.id, group.id);
        const session = sessionsByCell.get(key);
        return (
          <ScheduleGridCell
            key={group.id}
            cellId={key}
            session={session}
            isBreak={slot.is_break}
            isEditable={isEditable}
            isSelected={session !== undefined && session.id === selectedSessionId}
            isMoveTarget={isEditable && isMoveTarget(slot, group)}
            isHighlighted={highlightedCellKeys.has(key)}
            isBusy={isBusy}
            slotLabel={slotLabel}
            onSelect={() => {
              if (session !== undefined) {
                onSelectSession(session);
              }
            }}
            onPlace={() => {
              onPlaceInSlot(slot);
            }}
            onToggleLock={() => {
              if (session !== undefined) {
                onToggleLock(session);
              }
            }}
          />
        );
      })}
    </tr>
  );
}
