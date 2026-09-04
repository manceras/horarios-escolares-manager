import { useTranslation } from "react-i18next";

import type { Conflict, ConflictReport } from "@/features/schedules/api";
import { conflictId } from "@/features/schedules/schedule-grid";
import { cn } from "@/lib/utils";

export interface ConflictListProps {
  report: ConflictReport;
  /** Identity of the conflict currently highlighted in the grid, if any. */
  selectedConflictId: string | null;
  onSelectConflict: (conflict: Conflict, conflictId: string) => void;
}

/**
 * The hard-constraint violations of one schedule, each translated from its
 * `code` -- the backend `message` is English and meant for logs. Selecting a
 * conflict highlights the cells it points at.
 */
export function ConflictList({ report, selectedConflictId, onSelectConflict }: ConflictListProps) {
  const { t } = useTranslation();

  if (!report.has_conflicts) {
    return <p className="text-sm text-muted-foreground">{t("schedules.noConflicts")}</p>;
  }

  return (
    <ul className="space-y-1">
      {report.conflicts.map((conflict) => {
        const id = conflictId(conflict);
        return (
          <li key={id}>
            <button
              type="button"
              aria-pressed={id === selectedConflictId}
              className={cn(
                "w-full rounded-md border border-border p-2 text-left text-sm hover:bg-accent",
                id === selectedConflictId && "border-destructive",
              )}
              onClick={() => {
                onSelectConflict(conflict, id);
              }}
            >
              {t([`schedules.conflictCodes.${conflict.code}`, "schedules.conflictCodes.unknown"])}
            </button>
          </li>
        );
      })}
    </ul>
  );
}
