import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { QueryState } from "@/components/QueryState";
import { Button } from "@/components/ui/button";
import { useScheduleDetail, useSchedules, useTimeSlots } from "@/features/schedule-print/api";
import { buildCsv, downloadCsv } from "@/features/schedule-print/csv";
import { PrintableWeek } from "@/features/schedule-print/PrintableWeek";
import {
  buildWeekGrid,
  getViewEntities,
  WEEKDAYS,
  type ViewType,
} from "@/features/schedule-print/print-model";
import "@/features/schedule-print/schedule-print.css";
import { ViewSelector } from "@/features/schedule-print/ViewSelector";

/**
 * Printable and exportable views of a finished timetable: by teacher, by
 * class group or by room, one or all at once, on screen, on paper and as CSV.
 */
export function SchedulePrintPage() {
  const { t } = useTranslation();

  const schedulesQuery = useSchedules();
  const timeSlotsQuery = useTimeSlots();

  const [scheduleId, setScheduleId] = useState<number | undefined>(undefined);
  const [viewType, setViewType] = useState<ViewType>("teacher");
  const [selection, setSelection] = useState<number | "all">("all");

  // Default to the published schedule, if there is one -- that is the
  // timetable a school actually hands out.
  useEffect(() => {
    if (scheduleId !== undefined) return;
    const schedules = schedulesQuery.data;
    if (schedules === undefined) return;
    const first = schedules[0];
    if (first === undefined) return;
    const published = schedules.find((schedule) => schedule.status === "published");
    setScheduleId((published ?? first).id);
  }, [schedulesQuery.data, scheduleId]);

  const detailQuery = useScheduleDetail(scheduleId);

  function handleViewTypeChange(nextViewType: ViewType): void {
    setViewType(nextViewType);
    // An id from one axis has no meaning on another.
    setSelection("all");
  }

  const sessions = useMemo(() => detailQuery.data?.sessions ?? [], [detailQuery.data]);
  const timeSlots = useMemo(() => timeSlotsQuery.data ?? [], [timeSlotsQuery.data]);
  const entities = useMemo(() => getViewEntities(sessions, viewType), [sessions, viewType]);

  const selectedEntities =
    selection === "all" ? entities : entities.filter((entity) => entity.id === selection);

  const sheets = useMemo(
    () =>
      selectedEntities.map((entity) => ({
        entity,
        rows: buildWeekGrid(timeSlots, sessions, viewType, entity.id),
      })),
    [selectedEntities, timeSlots, sessions, viewType],
  );

  const currentSchedule = schedulesQuery.data?.find((schedule) => schedule.id === scheduleId);

  function headingFor(entityName: string): string {
    return t("print.sheetHeading", {
      schedule: currentSchedule?.name ?? "",
      scope: t(`print.viewType.${viewType}`),
      name: entityName,
    });
  }

  function handleExportCsv(): void {
    const weekdayLabels = WEEKDAYS.map(({ key }) => t(`app.weekdays.${key}`));
    const csv = buildCsv(
      sheets.map((sheet) => ({ title: headingFor(sheet.entity.name), rows: sheet.rows })),
      weekdayLabels,
      t("print.columns.time"),
      t("print.break"),
    );
    const filenameBase = `${currentSchedule?.name ?? "schedule"}-${viewType}`.replace(/\s+/g, "_");
    downloadCsv(`${filenameBase}.csv`, csv);
  }

  const isLoading = schedulesQuery.isLoading || timeSlotsQuery.isLoading || detailQuery.isLoading;
  const error = schedulesQuery.error ?? timeSlotsQuery.error ?? detailQuery.error;

  const hasError = error !== null;
  const hasNoSchedules = schedulesQuery.data !== undefined && schedulesQuery.data.length === 0;
  const hasNoSessions = !isLoading && !hasError && !hasNoSchedules && sheets.length === 0;

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between print:hidden">
        <h1 className="text-xl font-semibold">{t("print.title")}</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportCsv} disabled={sheets.length === 0}>
            {t("print.exportCsv")}
          </Button>
          <Button
            onClick={() => {
              window.print();
            }}
            disabled={sheets.length === 0}
          >
            {t("print.printButton")}
          </Button>
        </div>
      </div>

      <div className="print:hidden">
        <ViewSelector
          schedules={schedulesQuery.data ?? []}
          scheduleId={scheduleId}
          onScheduleChange={setScheduleId}
          viewType={viewType}
          onViewTypeChange={handleViewTypeChange}
          entities={entities}
          selection={selection}
          onSelectionChange={setSelection}
        />
      </div>

      <div className="print:hidden">
        <QueryState
          isLoading={isLoading}
          error={error}
          onRetry={() => {
            void schedulesQuery.refetch();
            void timeSlotsQuery.refetch();
            void detailQuery.refetch();
          }}
        />
      </div>

      {hasNoSchedules ? (
        <p className="text-sm text-muted-foreground print:hidden">{t("print.noSchedule")}</p>
      ) : null}

      {hasNoSessions ? (
        <p className="text-sm text-muted-foreground print:hidden">{t("print.noSessions")}</p>
      ) : null}

      <div className="space-y-8 print:space-y-0">
        {sheets.map((sheet, index) => (
          <PrintableWeek
            key={sheet.entity.id}
            heading={headingFor(sheet.entity.name)}
            rows={sheet.rows}
            breakAfter={index < sheets.length - 1}
          />
        ))}
      </div>
    </section>
  );
}
