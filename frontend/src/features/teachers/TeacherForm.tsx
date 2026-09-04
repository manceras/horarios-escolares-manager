import { useTranslation } from "react-i18next";

import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { UseEntityFormResult } from "@/lib/forms/useEntityForm";

import type { TeacherFormValues } from "./teacher-form-values";

interface TeacherFormProps {
  form: UseEntityFormResult<TeacherFormValues>;
}

/** Fields for the create/edit dialog. Rendered inside `<EntityDialog>`. */
export function TeacherForm({ form }: TeacherFormProps) {
  const { t } = useTranslation();
  const { values, errors, setField } = form;

  return (
    <>
      <div className="space-y-1.5">
        <Label htmlFor="teacher-first-name">{t("teachers.firstName")}</Label>
        <Input
          id="teacher-first-name"
          value={values.first_name}
          onChange={(event) => {
            setField("first_name", event.target.value);
          }}
        />
        {errors.first_name ? (
          <p className="text-sm text-destructive">{t(errors.first_name)}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="teacher-last-name">{t("teachers.lastName")}</Label>
        <Input
          id="teacher-last-name"
          value={values.last_name}
          onChange={(event) => {
            setField("last_name", event.target.value);
          }}
        />
        {errors.last_name ? (
          <p className="text-sm text-destructive">{t(errors.last_name)}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="teacher-email">{t("teachers.email")}</Label>
        <Input
          id="teacher-email"
          type="email"
          value={values.email}
          onChange={(event) => {
            setField("email", event.target.value);
          }}
        />
        {errors.email ? <p className="text-sm text-destructive">{t(errors.email)}</p> : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="teacher-max-periods">{t("teachers.maxPeriods")}</Label>
        <Input
          id="teacher-max-periods"
          type="number"
          min={1}
          value={values.max_periods_per_week}
          onChange={(event) => {
            setField("max_periods_per_week", Number(event.target.value));
          }}
        />
        {errors.max_periods_per_week ? (
          <p className="text-sm text-destructive">{t(errors.max_periods_per_week)}</p>
        ) : null}
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          id="teacher-is-specialist"
          checked={values.is_specialist}
          onCheckedChange={(checked) => {
            setField("is_specialist", checked === true);
          }}
        />
        <Label htmlFor="teacher-is-specialist">{t("teachers.specialist")}</Label>
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          id="teacher-active"
          checked={values.active}
          onCheckedChange={(checked) => {
            setField("active", checked === true);
          }}
        />
        <Label htmlFor="teacher-active">{t("teachers.active")}</Label>
      </div>
    </>
  );
}
