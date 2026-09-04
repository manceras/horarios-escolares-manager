import { CircleAlert, CircleCheck } from "lucide-react";
import { useTranslation } from "react-i18next";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { QueryState } from "@/components/QueryState";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { useWorkload } from "./api";
import type { GroupWorkload, TeacherWorkload } from "./api";

interface FitStatusProps {
  fits: boolean;
  hint: string;
}

/**
 * Fit/does-not-fit is never signalled by colour alone: an icon and a text
 * label carry the state, and a plain-language hint explains what to do when
 * it does not fit -- this report is the whole point of the screen.
 */
function FitStatus({ fits, hint }: FitStatusProps) {
  const { t } = useTranslation();

  if (fits) {
    return (
      <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <CircleCheck className="size-4" aria-hidden="true" />
        {t("workload.fits")}
      </span>
    );
  }

  return (
    <div className="space-y-1">
      <span className="flex items-center gap-1.5 text-sm font-medium text-destructive">
        <CircleAlert className="size-4" aria-hidden="true" />
        {t("workload.doesNotFit")}
      </span>
      <p className="text-xs text-muted-foreground">{hint}</p>
    </div>
  );
}

export function WorkloadPanel() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useWorkload();

  const groupColumns: DataTableColumn<GroupWorkload>[] = [
    { key: "classGroup", header: t("workload.classGroup"), cell: (row) => row.class_group_name },
    {
      key: "assigned",
      header: t("workload.assignedOfAvailable"),
      cell: (row) =>
        t("workload.periodsRatio", {
          assigned: row.assigned_periods,
          total: row.available_periods,
        }),
    },
    {
      key: "status",
      header: t("workload.status"),
      cell: (row) => <FitStatus fits={row.fits} hint={t("workload.groupHint")} />,
    },
  ];

  const teacherColumns: DataTableColumn<TeacherWorkload>[] = [
    { key: "teacher", header: t("workload.teacher"), cell: (row) => row.teacher_name },
    {
      key: "assigned",
      header: t("workload.assignedOfMax"),
      cell: (row) =>
        t("workload.periodsRatio", {
          assigned: row.assigned_periods,
          total: row.max_periods_per_week,
        }),
    },
    {
      key: "status",
      header: t("workload.status"),
      cell: (row) => <FitStatus fits={row.fits} hint={t("workload.teacherHint")} />,
    },
  ];

  return (
    <section className="space-y-2">
      <h2 className="text-lg font-semibold">{t("workload.title")}</h2>

      <QueryState
        isLoading={isLoading}
        error={error}
        onRetry={() => {
          void refetch();
        }}
      />

      {data ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>{t("workload.groupsTitle")}</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable
                columns={groupColumns}
                rows={data.groups}
                getRowId={(row) => row.class_group_id}
                emptyMessage={t("workload.groupsEmpty")}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("workload.teachersTitle")}</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable
                columns={teacherColumns}
                rows={data.teachers}
                getRowId={(row) => row.teacher_id}
                emptyMessage={t("workload.teachersEmpty")}
              />
            </CardContent>
          </Card>
        </div>
      ) : null}
    </section>
  );
}
