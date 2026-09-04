import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { QueryState } from "@/components/QueryState";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Conflict } from "@/features/schedules/api";
import {
  useClassGroups,
  useMoveSession,
  useSchedule,
  useScheduleConflicts,
  useSetSessionLock,
  useTimeSlots,
} from "@/features/schedules/api";
import { ConflictList } from "@/features/schedules/ConflictList";
import { GenerationPanel } from "@/features/schedules/GenerationPanel";
import { conflictCellKeys, getSessionEditErrorKeys } from "@/features/schedules/schedule-grid";
import { ScheduleGrid } from "@/features/schedules/ScheduleGrid";

export interface ScheduleWorkspaceProps {
  scheduleId: number;
}

const NO_HIGHLIGHT: ReadonlySet<string> = new Set<string>();

/**
 * One schedule end to end: run the solver, read the week, adjust it by hand and
 * see what is still broken. Only a draft is editable -- a published schedule is
 * what the school reads, and the API refuses every write to it.
 */
export function ScheduleWorkspace({ scheduleId }: ScheduleWorkspaceProps) {
  const { t } = useTranslation();

  const schedule = useSchedule(scheduleId);
  const conflicts = useScheduleConflicts(scheduleId);
  const timeSlots = useTimeSlots();
  const classGroups = useClassGroups();

  const moveSession = useMoveSession();
  const setSessionLock = useSetSessionLock();

  const [selected, setSelected] = useState<{ id: string; conflict: Conflict } | null>(null);

  const sessions = useMemo(() => schedule.data?.sessions ?? [], [schedule.data]);
  const sortedClassGroups = useMemo(
    () =>
      [...(classGroups.data ?? [])].sort(
        (left, right) => left.grade - right.grade || left.name.localeCompare(right.name),
      ),
    [classGroups.data],
  );
  const highlightedCellKeys = useMemo(
    () => (selected === null ? NO_HIGHLIGHT : conflictCellKeys(selected.conflict, sessions)),
    [selected, sessions],
  );

  const editError = moveSession.error ?? setSessionLock.error;
  const isBusy = moveSession.isPending || setSessionLock.isPending;

  if (schedule.data === undefined) {
    return (
      <QueryState
        isLoading={schedule.isLoading}
        error={schedule.error}
        onRetry={() => {
          void schedule.refetch();
        }}
      />
    );
  }

  const isEditable = schedule.data.status === "draft";

  return (
    <section className="space-y-4">
      <header className="space-y-1">
        <h1 className="text-xl font-semibold">{schedule.data.name}</h1>
        <p className="text-sm text-muted-foreground">
          {t(`schedules.statuses.${schedule.data.status}`)}
        </p>
      </header>

      {isEditable ? null : (
        <p className="rounded-md border border-border bg-muted p-3 text-sm">
          {t("schedules.readOnlyNotice")}
        </p>
      )}

      <GenerationPanel schedule={schedule.data} isEditable={isEditable} />

      {editError === null ? null : (
        <p role="alert" className="text-sm text-destructive">
          {t(getSessionEditErrorKeys(editError))}
        </p>
      )}

      {timeSlots.data && classGroups.data ? (
        <ScheduleGrid
          sessions={sessions}
          timeSlots={timeSlots.data}
          classGroups={sortedClassGroups}
          isEditable={isEditable}
          isBusy={isBusy}
          highlightedCellKeys={highlightedCellKeys}
          onMoveSession={(session, targetTimeSlot) => {
            moveSession.mutate({ scheduleId, sessionId: session.id, targetTimeSlot });
          }}
          onToggleLock={(session) => {
            setSessionLock.mutate({ scheduleId, sessionId: session.id, locked: !session.locked });
          }}
        />
      ) : (
        <QueryState
          isLoading={timeSlots.isLoading || classGroups.isLoading}
          error={timeSlots.error ?? classGroups.error}
          onRetry={() => {
            void timeSlots.refetch();
            void classGroups.refetch();
          }}
        />
      )}

      <Card>
        <CardHeader>
          <CardTitle>{t("schedules.conflictsTitle")}</CardTitle>
        </CardHeader>
        <CardContent>
          {conflicts.data ? (
            <ConflictList
              report={conflicts.data}
              selectedConflictId={selected?.id ?? null}
              onSelectConflict={(conflict, id) => {
                setSelected((current) => (current?.id === id ? null : { id, conflict }));
              }}
            />
          ) : (
            <QueryState
              isLoading={conflicts.isLoading}
              error={conflicts.error}
              onRetry={() => {
                void conflicts.refetch();
              }}
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
