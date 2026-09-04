import { useState } from "react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { TimeSlot } from "@/features/time-slots/api";
import { getErrorMessageKeys } from "@/lib/api/error-translation";
import { formatTime } from "@/lib/time-format";
import { cn } from "@/lib/utils";
import { WEEKDAY_INDICES, dayPeriodKey, weekdayTranslationKey } from "@/lib/weekdays";

import type { useReplaceTeacherUnavailabilities } from "./api";

interface TeacherAvailabilityGridProps {
  timeSlots: readonly TimeSlot[];
  initialUnavailableSlotIds: readonly number[];
  replaceUnavailabilities: ReturnType<typeof useReplaceTeacherUnavailabilities>;
}

function setsEqual(a: ReadonlySet<number>, b: ReadonlySet<number>): boolean {
  return a.size === b.size && [...a].every((value) => b.has(value));
}

/**
 * The whole week as a grid of checkboxes for one teacher: checked means
 * available, unchecked means the teacher cannot teach that slot. Edits stay
 * local until "Save" replaces the teacher's whole unavailability set in one
 * request -- never one request per checkbox.
 */
export function TeacherAvailabilityGrid({
  timeSlots,
  initialUnavailableSlotIds,
  replaceUnavailabilities,
}: TeacherAvailabilityGridProps) {
  const { t } = useTranslation();
  const [unavailableSlotIds, setUnavailableSlotIds] = useState<Set<number>>(
    () => new Set(initialUnavailableSlotIds),
  );
  const [committedSlotIds, setCommittedSlotIds] = useState<Set<number>>(
    () => new Set(initialUnavailableSlotIds),
  );

  const isDirty = !setsEqual(unavailableSlotIds, committedSlotIds);
  const hasError = replaceUnavailabilities.error !== null;

  function toggleAvailable(slotId: number, available: boolean): void {
    setUnavailableSlotIds((previous) => {
      const next = new Set(previous);
      if (available) {
        next.delete(slotId);
      } else {
        next.add(slotId);
      }
      return next;
    });
  }

  function handleSave(): void {
    const ids = [...unavailableSlotIds];
    replaceUnavailabilities.mutate(ids, {
      onSuccess: () => {
        setCommittedSlotIds(new Set(ids));
      },
    });
  }

  const periods = [...new Set(timeSlots.map((slot) => slot.period_index))].sort((a, b) => a - b);
  const slotByDayAndPeriod = new Map<string, TimeSlot>();
  for (const slot of timeSlots) {
    slotByDayAndPeriod.set(dayPeriodKey(slot.day_of_week, slot.period_index), slot);
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-md border border-border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("timeSlots.periodIndex")}</TableHead>
              {WEEKDAY_INDICES.map((day) => (
                <TableHead key={day}>{t(weekdayTranslationKey(day))}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {periods.map((period) => (
              <TableRow key={period}>
                <TableCell className="font-medium">{period + 1}</TableCell>
                {WEEKDAY_INDICES.map((day) => {
                  const slot = slotByDayAndPeriod.get(dayPeriodKey(day, period));
                  return (
                    <TableCell key={day} className="align-top">
                      {slot ? (
                        <AvailabilityCell
                          timeSlot={slot}
                          isUnavailable={unavailableSlotIds.has(slot.id)}
                          onToggle={toggleAvailable}
                        />
                      ) : (
                        <span className="text-sm text-muted-foreground">—</span>
                      )}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {hasError ? (
        <p className="text-sm text-destructive">
          {t(getErrorMessageKeys(replaceUnavailabilities.error))}
        </p>
      ) : null}

      <Button disabled={!isDirty || replaceUnavailabilities.isPending} onClick={handleSave}>
        {replaceUnavailabilities.isPending ? t("app.saving") : t("app.save")}
      </Button>
    </div>
  );
}

interface AvailabilityCellProps {
  timeSlot: TimeSlot;
  isUnavailable: boolean;
  onToggle: (slotId: number, available: boolean) => void;
}

function AvailabilityCell({ timeSlot, isUnavailable, onToggle }: AvailabilityCellProps) {
  const { t } = useTranslation();

  if (timeSlot.is_break) {
    return (
      <div className="rounded-md border border-dashed border-muted-foreground/40 bg-muted px-2 py-1.5 text-xs text-muted-foreground">
        {t("timeSlots.isBreak")}
      </div>
    );
  }

  return (
    <label
      className={cn(
        "flex cursor-pointer items-center gap-2 rounded-md border border-border px-2 py-1.5 text-sm",
        isUnavailable && "bg-muted",
      )}
    >
      <Checkbox
        checked={!isUnavailable}
        onCheckedChange={(checked) => {
          onToggle(timeSlot.id, checked === true);
        }}
      />
      <span>{`${formatTime(timeSlot.start_time)}–${formatTime(timeSlot.end_time)}`}</span>
    </label>
  );
}
