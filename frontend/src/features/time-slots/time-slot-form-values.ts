import type { EntityFormValidator } from "@/lib/forms/useEntityForm";

/** Plain values a time slot form edits -- shared shape for both create and edit. */
export interface TimeSlotFormValues {
  day_of_week: number;
  period_index: number;
  start_time: string;
  end_time: string;
  is_break: boolean;
}

export const emptyTimeSlotFormValues: TimeSlotFormValues = {
  day_of_week: 0,
  period_index: 0,
  start_time: "09:00",
  end_time: "09:45",
  is_break: false,
};

export const validateTimeSlotForm: EntityFormValidator<TimeSlotFormValues> = (values) => {
  const errors: Partial<Record<keyof TimeSlotFormValues, string>> = {};
  if (!Number.isInteger(values.day_of_week) || values.day_of_week < 0 || values.day_of_week > 4) {
    errors.day_of_week = "timeSlots.validation.dayOfWeekInvalid";
  }
  if (!Number.isInteger(values.period_index) || values.period_index < 0) {
    errors.period_index = "timeSlots.validation.periodIndexInvalid";
  }
  if (values.start_time.trim() === "") {
    errors.start_time = "timeSlots.validation.startTimeRequired";
  }
  if (values.end_time.trim() === "") {
    errors.end_time = "timeSlots.validation.endTimeRequired";
  }
  if (
    values.start_time.trim() !== "" &&
    values.end_time.trim() !== "" &&
    values.end_time <= values.start_time
  ) {
    errors.end_time = "timeSlots.validation.endTimeBeforeStart";
  }
  return errors;
};
