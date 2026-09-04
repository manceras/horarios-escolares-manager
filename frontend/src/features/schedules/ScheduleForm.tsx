import { useTranslation } from "react-i18next";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { UseEntityFormResult } from "@/lib/forms/useEntityForm";

import type { ScheduleFormValues } from "./schedule-form-values";

interface ScheduleFormProps {
  form: UseEntityFormResult<ScheduleFormValues>;
}

/** Fields for the create dialog. Rendered inside `<EntityDialog>`. */
export function ScheduleForm({ form }: ScheduleFormProps) {
  const { t } = useTranslation();
  const { values, errors, setField } = form;

  return (
    <div className="space-y-1.5">
      <Label htmlFor="schedule-name">{t("schedules.name")}</Label>
      <Input
        id="schedule-name"
        value={values.name}
        onChange={(event) => {
          setField("name", event.target.value);
        }}
      />
      {errors.name ? <p className="text-sm text-destructive">{t(errors.name)}</p> : null}
    </div>
  );
}
