import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router-dom";

import { ScheduleWorkspace } from "@/features/schedules/ScheduleWorkspace";

/** One schedule: the generation panel, the weekly grid and its conflicts. */
export function SchedulePage() {
  const { t } = useTranslation();
  const { scheduleId } = useParams();
  const parsedScheduleId = Number(scheduleId);

  return (
    <div className="space-y-4">
      <Link className="text-sm text-muted-foreground hover:text-primary" to="/schedules">
        {t("schedules.backToList")}
      </Link>
      {Number.isInteger(parsedScheduleId) && parsedScheduleId > 0 ? (
        <ScheduleWorkspace scheduleId={parsedScheduleId} />
      ) : (
        <p className="text-sm text-destructive">{t("errors.not_found")}</p>
      )}
    </div>
  );
}
