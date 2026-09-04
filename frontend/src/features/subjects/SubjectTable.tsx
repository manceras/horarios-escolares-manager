import { useTranslation } from "react-i18next";

import { DataTable, type DataTableColumn } from "@/components/DataTable";

import type { Subject } from "./api";

interface SubjectTableProps {
  subjects: readonly Subject[];
  onEdit: (subject: Subject) => void;
  onDelete: (subject: Subject) => void;
}

export function SubjectTable({ subjects, onEdit, onDelete }: SubjectTableProps) {
  const { t } = useTranslation();

  const columns: DataTableColumn<Subject>[] = [
    { key: "code", header: t("subjects.code"), cell: (subject) => subject.code },
    { key: "name", header: t("subjects.name"), cell: (subject) => subject.name },
    {
      key: "requiredRoomType",
      header: t("subjects.requiredRoomType"),
      cell: (subject) =>
        subject.required_room_type
          ? t(`rooms.types.${subject.required_room_type}`)
          : t("subjects.noRequiredRoomType"),
    },
  ];

  return (
    <DataTable
      columns={columns}
      rows={subjects}
      getRowId={(subject) => subject.id}
      emptyMessage={t("subjects.empty")}
      onEdit={onEdit}
      onDelete={onDelete}
    />
  );
}
