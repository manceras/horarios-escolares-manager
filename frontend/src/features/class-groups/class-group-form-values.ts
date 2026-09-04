import type { EntityFormValidator } from "@/lib/forms/useEntityForm";

/** Plain values a class group form edits -- shared shape for both create and edit. */
export interface ClassGroupFormValues {
  name: string;
  grade: number;
  tutor_id: number | null;
  home_room_id: number | null;
}

export const emptyClassGroupFormValues: ClassGroupFormValues = {
  name: "",
  grade: 1,
  tutor_id: null,
  home_room_id: null,
};

export const validateClassGroupForm: EntityFormValidator<ClassGroupFormValues> = (values) => {
  const errors: Partial<Record<keyof ClassGroupFormValues, string>> = {};
  if (values.name.trim() === "") {
    errors.name = "classGroups.validation.nameRequired";
  }
  if (!Number.isInteger(values.grade) || values.grade < 1 || values.grade > 6) {
    errors.grade = "classGroups.validation.gradeInvalid";
  }
  return errors;
};
