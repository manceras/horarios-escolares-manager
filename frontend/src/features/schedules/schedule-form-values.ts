import type { EntityFormValidator } from "@/lib/forms/useEntityForm";

/** A schedule is created empty; only its name is entered by hand. */
export interface ScheduleFormValues {
  name: string;
}

export const emptyScheduleFormValues: ScheduleFormValues = {
  name: "",
};

export const validateScheduleForm: EntityFormValidator<ScheduleFormValues> = (values) => {
  const errors: Partial<Record<keyof ScheduleFormValues, string>> = {};
  if (values.name.trim() === "") {
    errors.name = "schedules.validation.nameRequired";
  }
  return errors;
};
