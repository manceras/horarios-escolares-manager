import { Lock, Unlock } from "lucide-react";
import { useTranslation } from "react-i18next";

import type { ScheduledSession } from "@/features/schedules/api";
import { cn } from "@/lib/utils";

export interface ScheduleGridCellProps {
  /** `(time slot, class group)` key of this cell, used to scroll a conflict into view. */
  cellId: string;
  session: ScheduledSession | undefined;
  isBreak: boolean;
  isEditable: boolean;
  isSelected: boolean;
  /** The selected session may be dropped here: same class group, empty, teaching slot. */
  isMoveTarget: boolean;
  isHighlighted: boolean;
  isBusy: boolean;
  /** Label of the slot this cell sits in, for the move button's accessible name. */
  slotLabel: string;
  onSelect: () => void;
  onPlace: () => void;
  onToggleLock: () => void;
}

/**
 * One (time slot, class group) cell. It never decides what a legal move is --
 * the page passes `isMoveTarget` and the server has the last word -- it only
 * renders the session and the two things a human can do to it.
 */
export function ScheduleGridCell({
  cellId,
  session,
  isBreak,
  isEditable,
  isSelected,
  isMoveTarget,
  isHighlighted,
  isBusy,
  slotLabel,
  onSelect,
  onPlace,
  onToggleLock,
}: ScheduleGridCellProps) {
  const { t } = useTranslation();

  if (isBreak) {
    return (
      <td data-cell-key={cellId} className="border border-border bg-muted p-0">
        <span className="sr-only">{t("schedules.breakSlot")}</span>
      </td>
    );
  }

  if (isMoveTarget) {
    return (
      <td data-cell-key={cellId} className="border border-dashed border-primary p-0">
        <button
          type="button"
          className="flex size-full min-h-16 items-center justify-center px-1 py-2 text-xs font-medium text-primary hover:bg-accent disabled:opacity-50"
          onClick={onPlace}
          disabled={isBusy}
        >
          {t("schedules.moveHere", { slot: slotLabel })}
        </button>
      </td>
    );
  }

  if (session === undefined) {
    return <td data-cell-key={cellId} className="border border-border p-0" />;
  }

  return (
    <td
      data-cell-key={cellId}
      className={cn(
        "border border-border p-0 align-top",
        session.locked && "border-l-4 border-l-primary bg-accent",
        isSelected && "ring-2 ring-inset ring-primary",
        isHighlighted && "ring-2 ring-inset ring-destructive",
      )}
    >
      <div className="flex min-h-16 flex-col gap-0.5 p-1.5 text-xs">
        <div className="flex items-start gap-1">
          <span className="font-semibold" title={session.subject_name}>
            {session.subject_code}
          </span>
          {session.locked ? (
            <Lock
              aria-label={t("schedules.lockedSession")}
              className="ml-auto size-3 text-primary"
            />
          ) : null}
        </div>
        <span className="truncate text-muted-foreground" title={session.teacher_name}>
          {session.teacher_name}
        </span>
        <span className="truncate text-muted-foreground">
          {session.room_name ?? t("schedules.noRoom")}
        </span>

        {isEditable ? (
          <div className="mt-auto flex items-center gap-1 pt-1">
            <button
              type="button"
              aria-pressed={isSelected}
              className="rounded border border-border px-1.5 py-0.5 text-xs hover:bg-accent disabled:opacity-50"
              onClick={onSelect}
              disabled={isBusy}
            >
              {isSelected ? t("schedules.cancelMove") : t("schedules.move")}
            </button>
            <button
              type="button"
              aria-pressed={session.locked}
              aria-label={session.locked ? t("schedules.unlock") : t("schedules.lock")}
              title={session.locked ? t("schedules.unlock") : t("schedules.lock")}
              className="rounded border border-border p-1 hover:bg-accent disabled:opacity-50"
              onClick={onToggleLock}
              disabled={isBusy}
            >
              {session.locked ? <Unlock className="size-3" /> : <Lock className="size-3" />}
            </button>
          </div>
        ) : null}
      </div>
    </td>
  );
}
