import type { EntityFormValidator } from "@/lib/forms/useEntityForm";

/** Plain values a teacher form edits -- shared shape for both create and edit. */
export interface TeacherFormValues {
  first_name: string;
  last_name: string;
  email: string;
  is_specialist: boolean;
  max_periods_per_week: number;
  active: boolean;
}

export const emptyTeacherFormValues: TeacherFormValues = {
  first_name: "",
  last_name: "",
  email: "",
  is_specialist: false,
  max_periods_per_week: 25,
  active: true,
};

export const validateTeacherForm: EntityFormValidator<TeacherFormValues> = (values) => {
  const errors: Partial<Record<keyof TeacherFormValues, string>> = {};
  if (values.first_name.trim() === "") {
    errors.first_name = "teachers.validation.firstNameRequired";
  }
  if (values.last_name.trim() === "") {
    errors.last_name = "teachers.validation.lastNameRequired";
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    errors.email = "teachers.validation.emailInvalid";
  }
  if (!Number.isInteger(values.max_periods_per_week) || values.max_periods_per_week <= 0) {
    errors.max_periods_per_week = "teachers.validation.maxPeriodsInvalid";
  }
  return errors;
};
