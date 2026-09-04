import { useState } from "react";
import { useTranslation } from "react-i18next";

import type { GenerationResult, ScheduleDetail } from "@/features/schedules/api";
import { useGenerateSchedule } from "@/features/schedules/api";
import { Button } from "@/components/ui/button";
import { getErrorMessageKeys } from "@/lib/api/error-translation";

export interface GenerationPanelProps {
  schedule: ScheduleDetail;
  /** Only a draft may be generated; a published schedule is archived, not rebuilt. */
  isEditable: boolean;
}

/**
 * Runs the solver and reports the outcome. Generation is synchronous and can
 * take seconds, so the button owns a busy state; an infeasible run is not an
 * error but an answer, and the solver's own message is the only clue the user
 * gets about which constraint cannot be met, so it is shown verbatim.
 */
export function GenerationPanel({ schedule, isEditable }: GenerationPanelProps) {
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<GenerationResult | null>(null);
  const generateSchedule = useGenerateSchedule();

  const solverStatus = result?.solver_status ?? schedule.solver_status;
  const generatedAt = result?.generated_at ?? schedule.generated_at;

  function handleGenerate(): void {
    generateSchedule.mutate(schedule.id, { onSuccess: setResult });
  }

  return (
    <div className="space-y-3 rounded-md border border-border p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-medium">{t("schedules.generationTitle")}</h2>
          <p className="text-sm text-muted-foreground">{t("schedules.generationHint")}</p>
        </div>
        {isEditable ? (
          <Button onClick={handleGenerate} disabled={generateSchedule.isPending}>
            {generateSchedule.isPending ? t("schedules.generating") : t("schedules.generate")}
          </Button>
        ) : null}
      </div>

      <dl className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm sm:grid-cols-3">
        <div>
          <dt className="text-muted-foreground">{t("schedules.solverStatusLabel")}</dt>
          <dd>
            {solverStatus === null || solverStatus === undefined
              ? t("schedules.neverGenerated")
              : t([`schedules.solverStatus.${solverStatus}`, "schedules.solverStatus.unknown"])}
          </dd>
        </div>
        <div>
          <dt className="text-muted-foreground">{t("schedules.sessionsPlaced")}</dt>
          <dd>{result?.sessions_placed ?? schedule.sessions.length}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">{t("schedules.generatedAt")}</dt>
          <dd>
            {generatedAt === null || generatedAt === undefined
              ? t("schedules.neverGenerated")
              : new Date(generatedAt).toLocaleString(i18n.language)}
          </dd>
        </div>
      </dl>

      {result !== null && !result.solved ? (
        <div role="alert" className="rounded-md border border-destructive p-3 text-sm">
          <p className="font-medium text-destructive">{t("schedules.infeasibleTitle")}</p>
          <p className="text-muted-foreground">{t("schedules.infeasibleHint")}</p>
          {result.message === "" ? null : (
            <p className="mt-2 font-mono text-xs break-words">{result.message}</p>
          )}
        </div>
      ) : null}

      {generateSchedule.error !== null ? (
        <p role="alert" className="text-sm text-destructive">
          {t(getErrorMessageKeys(generateSchedule.error))}
        </p>
      ) : null}
    </div>
  );
}
