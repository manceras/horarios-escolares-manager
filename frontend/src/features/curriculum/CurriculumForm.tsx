import { useTranslation } from "react-i18next";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toApiError } from "@/lib/api/client";
import type { UseEntityFormResult } from "@/lib/forms/useEntityForm";

import type { ClassGroup, Subject } from "./api";
import type { CurriculumFormValues } from "./curriculum-form-values";

/** A teacher, narrowed to what a select option needs. */
export interface TeacherOption {
  id: number;
  first_name: string;
  last_name: string;
}

interface CurriculumFormProps {
  form: UseEntityFormResult<CurriculumFormValues>;
  classGroups: readonly ClassGroup[];
  subjects: readonly Subject[];
  teachers: readonly TeacherOption[];
  /**
   * The create/update mutation's `error`, if the last submit failed. The
   * dialog around this form already shows the generic translated message
   * for the error `code`; when the backend rejected the entry because it
   * does not fit (a `validation_error` naming the group or teacher and both
   * numbers), that specific sentence is shown here too so it is not
   * swallowed by the generic banner.
   */
  submitError?: unknown;
}

/** Fields for the create/edit dialog. Rendered inside `<EntityDialog>`. */
export function CurriculumForm({
  form,
  classGroups,
  subjects,
  teachers,
  submitError,
}: CurriculumFormProps) {
  const { t } = useTranslation();
  const { values, errors, setField } = form;

  const apiError =
    submitError !== null && submitError !== undefined ? toApiError(submitError) : null;
  const showServerDetail = apiError !== null && apiError.code === "validation_error";

  return (
    <>
      <div className="space-y-1.5">
        <Label htmlFor="curriculum-class-group">{t("curriculum.classGroup")}</Label>
        <Select
          {...(values.class_group_id > 0 ? { value: String(values.class_group_id) } : {})}
          onValueChange={(value) => {
            setField("class_group_id", Number(value));
          }}
        >
          <SelectTrigger id="curriculum-class-group" className="w-full">
            <SelectValue placeholder={t("curriculum.selectPlaceholder")} />
          </SelectTrigger>
          <SelectContent>
            {classGroups.map((group) => (
              <SelectItem key={group.id} value={String(group.id)}>
                {group.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.class_group_id ? (
          <p className="text-sm text-destructive">{t(errors.class_group_id)}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="curriculum-subject">{t("curriculum.subject")}</Label>
        <Select
          {...(values.subject_id > 0 ? { value: String(values.subject_id) } : {})}
          onValueChange={(value) => {
            setField("subject_id", Number(value));
          }}
        >
          <SelectTrigger id="curriculum-subject" className="w-full">
            <SelectValue placeholder={t("curriculum.selectPlaceholder")} />
          </SelectTrigger>
          <SelectContent>
            {subjects.map((subject) => (
              <SelectItem key={subject.id} value={String(subject.id)}>
                {subject.code} — {subject.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.subject_id ? (
          <p className="text-sm text-destructive">{t(errors.subject_id)}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="curriculum-teacher">{t("curriculum.teacher")}</Label>
        <Select
          {...(values.teacher_id > 0 ? { value: String(values.teacher_id) } : {})}
          onValueChange={(value) => {
            setField("teacher_id", Number(value));
          }}
        >
          <SelectTrigger id="curriculum-teacher" className="w-full">
            <SelectValue placeholder={t("curriculum.selectPlaceholder")} />
          </SelectTrigger>
          <SelectContent>
            {teachers.map((teacher) => (
              <SelectItem key={teacher.id} value={String(teacher.id)}>
                {teacher.first_name} {teacher.last_name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.teacher_id ? (
          <p className="text-sm text-destructive">{t(errors.teacher_id)}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="curriculum-periods">{t("curriculum.periodsPerWeek")}</Label>
        <Input
          id="curriculum-periods"
          type="number"
          min={1}
          value={values.periods_per_week}
          onChange={(event) => {
            setField("periods_per_week", Number(event.target.value));
          }}
        />
        {errors.periods_per_week ? (
          <p className="text-sm text-destructive">{t(errors.periods_per_week)}</p>
        ) : null}
      </div>

      {showServerDetail ? (
        <p className="text-sm text-destructive">
          {t("curriculum.validation.serverDetail", { detail: apiError.detail })}
        </p>
      ) : null}
    </>
  );
}
