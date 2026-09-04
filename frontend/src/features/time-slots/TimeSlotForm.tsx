import { useTranslation } from "react-i18next";

import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { WEEKDAY_INDICES, weekdayTranslationKey } from "@/lib/weekdays";
import type { UseEntityFormResult } from "@/lib/forms/useEntityForm";

import type { TimeSlotFormValues } from "./time-slot-form-values";

interface TimeSlotFormProps {
  form: UseEntityFormResult<TimeSlotFormValues>;
}

/** Fields for the create/edit dialog. Rendered inside `<EntityDialog>`. */
export function TimeSlotForm({ form }: TimeSlotFormProps) {
  const { t } = useTranslation();
  const { values, errors, setField } = form;

  return (
    <>
      <div className="space-y-1.5">
        <Label htmlFor="time-slot-day">{t("timeSlots.dayOfWeek")}</Label>
        <Select
          value={String(values.day_of_week)}
          onValueChange={(value) => {
            setField("day_of_week", Number(value));
          }}
        >
          <SelectTrigger id="time-slot-day" className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {WEEKDAY_INDICES.map((day) => (
              <SelectItem key={day} value={String(day)}>
                {t(weekdayTranslationKey(day))}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.day_of_week ? (
          <p className="text-sm text-destructive">{t(errors.day_of_week)}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="time-slot-period">{t("timeSlots.periodIndex")}</Label>
        <Input
          id="time-slot-period"
          type="number"
          min={0}
          value={values.period_index}
          onChange={(event) => {
            setField("period_index", Number(event.target.value));
          }}
        />
        {errors.period_index ? (
          <p className="text-sm text-destructive">{t(errors.period_index)}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="time-slot-start">{t("timeSlots.startTime")}</Label>
        <Input
          id="time-slot-start"
          type="time"
          value={values.start_time}
          onChange={(event) => {
            setField("start_time", event.target.value);
          }}
        />
        {errors.start_time ? (
          <p className="text-sm text-destructive">{t(errors.start_time)}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="time-slot-end">{t("timeSlots.endTime")}</Label>
        <Input
          id="time-slot-end"
          type="time"
          value={values.end_time}
          onChange={(event) => {
            setField("end_time", event.target.value);
          }}
        />
        {errors.end_time ? <p className="text-sm text-destructive">{t(errors.end_time)}</p> : null}
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          id="time-slot-is-break"
          checked={values.is_break}
          onCheckedChange={(checked) => {
            setField("is_break", checked === true);
          }}
        />
        <Label htmlFor="time-slot-is-break">{t("timeSlots.isBreak")}</Label>
      </div>
    </>
  );
}
