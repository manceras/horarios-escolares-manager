import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { Button } from "@/components/ui/button";

import type { Schedule } from "./api";

interface ScheduleTableProps {
  schedules: readonly Schedule[];
  onPublish: (schedule: Schedule) => void;
  onDelete: (schedule: Schedule) => void;
}

export function ScheduleTable({ schedules, onPublish, onDelete }: ScheduleTableProps) {
  const { t, i18n } = useTranslation();

  function formatDate(value: string | null | undefined): string {
    return value === null || value === undefined
      ? t("schedules.neverGenerated")
      : new Date(value).toLocaleString(i18n.language);
  }

  const columns: DataTableColumn<Schedule>[] = [
    {
      key: "name",
      header: t("schedules.name"),
      cell: (schedule) => (
        <Link className="font-medium hover:text-primary" to={`/schedules/${String(schedule.id)}`}>
          {schedule.name}
        </Link>
      ),
    },
    {
      key: "status",
      header: t("schedules.status"),
      cell: (schedule) => t(`schedules.statuses.${schedule.status}`),
    },
    {
      key: "createdAt",
      header: t("schedules.createdAt"),
      cell: (schedule) => formatDate(schedule.created_at),
    },
    {
      key: "generatedAt",
      header: t("schedules.generatedAt"),
      cell: (schedule) => formatDate(schedule.generated_at),
    },
    {
      key: "publish",
      header: t("schedules.publish"),
      cell: (schedule) =>
        schedule.status === "draft" ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => {
              onPublish(schedule);
            }}
          >
            {t("schedules.publish")}
          </Button>
        ) : null,
    },
  ];

  return (
    <DataTable
      columns={columns}
      rows={schedules}
      getRowId={(schedule) => schedule.id}
      emptyMessage={t("schedules.empty")}
      onDelete={onDelete}
    />
  );
}
