import { useTranslation } from "react-i18next";

import { DataTable, type DataTableColumn } from "@/components/DataTable";

import type { Teacher } from "./api";

interface TeacherTableProps {
  teachers: readonly Teacher[];
  onEdit: (teacher: Teacher) => void;
  onDelete: (teacher: Teacher) => void;
}

export function TeacherTable({ teachers, onEdit, onDelete }: TeacherTableProps) {
  const { t } = useTranslation();

  const columns: DataTableColumn<Teacher>[] = [
    {
      key: "name",
      header: t("teachers.name"),
      cell: (teacher) => `${teacher.first_name} ${teacher.last_name}`,
    },
    { key: "email", header: t("teachers.email"), cell: (teacher) => teacher.email },
    {
      key: "specialist",
      header: t("teachers.specialist"),
      cell: (teacher) => (teacher.is_specialist ? t("app.yes") : t("app.no")),
    },
    {
      key: "maxPeriods",
      header: t("teachers.maxPeriods"),
      cell: (teacher) => teacher.max_periods_per_week,
    },
    {
      key: "active",
      header: t("teachers.active"),
      cell: (teacher) => (teacher.active ? t("app.yes") : t("app.no")),
    },
  ];

  return (
    <DataTable
      columns={columns}
      rows={teachers}
      getRowId={(teacher) => teacher.id}
      emptyMessage={t("teachers.empty")}
      onEdit={onEdit}
      onDelete={onDelete}
    />
  );
}
