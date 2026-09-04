import type { RoomType } from "@/features/rooms/api";
import type { EntityFormValidator } from "@/lib/forms/useEntityForm";

/** Plain values a subject form edits -- shared shape for both create and edit. */
export interface SubjectFormValues {
  code: string;
  name: string;
  required_room_type: RoomType | null;
}

export const emptySubjectFormValues: SubjectFormValues = {
  code: "",
  name: "",
  required_room_type: null,
};

export const validateSubjectForm: EntityFormValidator<SubjectFormValues> = (values) => {
  const errors: Partial<Record<keyof SubjectFormValues, string>> = {};
  if (values.code.trim() === "") {
    errors.code = "subjects.validation.codeRequired";
  }
  if (values.name.trim() === "") {
    errors.name = "subjects.validation.nameRequired";
  }
  return errors;
};
