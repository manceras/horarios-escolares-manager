import type { EntityFormValidator } from "@/lib/forms/useEntityForm";

/**
 * Plain values a curriculum entry form edits. The three foreign keys use `0`
 * as the "nothing selected yet" sentinel -- database ids start at 1, so `0`
 * can never be a real option and the validator rejects it like any other
 * missing field.
 */
export interface CurriculumFormValues {
  class_group_id: number;
  subject_id: number;
  teacher_id: number;
  periods_per_week: number;
}

export const emptyCurriculumFormValues: CurriculumFormValues = {
  class_group_id: 0,
  subject_id: 0,
  teacher_id: 0,
  periods_per_week: 1,
};

export const validateCurriculumForm: EntityFormValidator<CurriculumFormValues> = (values) => {
  const errors: Partial<Record<keyof CurriculumFormValues, string>> = {};
  if (values.class_group_id <= 0) {
    errors.class_group_id = "curriculum.validation.classGroupRequired";
  }
  if (values.subject_id <= 0) {
    errors.subject_id = "curriculum.validation.subjectRequired";
  }
  if (values.teacher_id <= 0) {
    errors.teacher_id = "curriculum.validation.teacherRequired";
  }
  if (!Number.isInteger(values.periods_per_week) || values.periods_per_week < 1) {
    errors.periods_per_week = "curriculum.validation.periodsInvalid";
  }
  return errors;
};
