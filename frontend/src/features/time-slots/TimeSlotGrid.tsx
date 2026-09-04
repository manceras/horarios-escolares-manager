import { Pencil, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { formatTime } from "@/lib/time-format";
import { WEEKDAY_INDICES, dayPeriodKey, weekdayTranslationKey } from "@/lib/weekdays";

import type { TimeSlot } from "./api";

interface TimeSlotGridProps {
  timeSlots: readonly TimeSlot[];
  onEdit: (timeSlot: TimeSlot) => void;
  onDelete: (timeSlot: TimeSlot) => void;
}

/**
 * The week as a grid instead of a flat 30-row list: one column per weekday,
 * one row per period. Break slots (recreo) are visually distinct -- nothing
 * is ever scheduled in them.
 */
export function TimeSlotGrid({ timeSlots, onEdit, onDelete }: TimeSlotGridProps) {
  const { t } = useTranslation();

  if (timeSlots.length === 0) {
    return <p className="text-sm text-muted-foreground">{t("timeSlots.empty")}</p>;
  }

  const periods = [...new Set(timeSlots.map((slot) => slot.period_index))].sort((a, b) => a - b);
  const slotByDayAndPeriod = new Map<string, TimeSlot>();
  for (const slot of timeSlots) {
    slotByDayAndPeriod.set(dayPeriodKey(slot.day_of_week, slot.period_index), slot);
  }

  return (
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
                      <TimeSlotCell timeSlot={slot} onEdit={onEdit} onDelete={onDelete} />
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
  );
}

interface TimeSlotCellProps {
  timeSlot: TimeSlot;
  onEdit: (timeSlot: TimeSlot) => void;
  onDelete: (timeSlot: TimeSlot) => void;
}

function TimeSlotCell({ timeSlot, onEdit, onDelete }: TimeSlotCellProps) {
  const { t } = useTranslation();

  return (
    <div
      className={cn(
        "flex items-center justify-between gap-2 rounded-md border px-2 py-1.5",
        timeSlot.is_break
          ? "border-dashed border-muted-foreground/40 bg-muted"
          : "border-border bg-card",
      )}
    >
      <div className="text-sm">
        <p>{`${formatTime(timeSlot.start_time)}–${formatTime(timeSlot.end_time)}`}</p>
        {timeSlot.is_break ? (
          <p className="text-xs font-medium text-muted-foreground">{t("timeSlots.isBreak")}</p>
        ) : null}
      </div>
      <div className="flex shrink-0 gap-1">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          aria-label={t("actions.edit")}
          onClick={() => {
            onEdit(timeSlot);
          }}
        >
          <Pencil className="size-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          aria-label={t("actions.delete")}
          onClick={() => {
            onDelete(timeSlot);
          }}
        >
          <Trash2 className="size-4" />
        </Button>
      </div>
    </div>
  );
}
