import { useTranslation } from "react-i18next";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { useTeachers } from "@/features/teachers/api";

import type { ClassGroup } from "./api";
import { useRoomOptions } from "./api";

interface ClassGroupTableProps {
  classGroups: readonly ClassGroup[];
  onEdit: (classGroup: ClassGroup) => void;
  onDelete: (classGroup: ClassGroup) => void;
}

export function ClassGroupTable({ classGroups, onEdit, onDelete }: ClassGroupTableProps) {
  const { t } = useTranslation();
  const { data: teachers } = useTeachers();
  const { data: rooms } = useRoomOptions();

  function tutorName(classGroup: ClassGroup): string {
    if (classGroup.tutor_id === null || classGroup.tutor_id === undefined) {
      return t("classGroups.unassigned");
    }
    const tutor = teachers?.find((teacher) => teacher.id === classGroup.tutor_id);
    return tutor ? `${tutor.first_name} ${tutor.last_name}` : t("classGroups.unassigned");
  }

  function homeRoomName(classGroup: ClassGroup): string {
    if (classGroup.home_room_id === null || classGroup.home_room_id === undefined) {
      return t("classGroups.unassigned");
    }
    const room = rooms?.find((candidate) => candidate.id === classGroup.home_room_id);
    return room ? room.name : t("classGroups.unassigned");
  }

  const columns: DataTableColumn<ClassGroup>[] = [
    { key: "name", header: t("classGroups.name"), cell: (classGroup) => classGroup.name },
    { key: "grade", header: t("classGroups.grade"), cell: (classGroup) => classGroup.grade },
    { key: "tutor", header: t("classGroups.tutor"), cell: tutorName },
    { key: "homeRoom", header: t("classGroups.homeRoom"), cell: homeRoomName },
  ];

  return (
    <DataTable
      columns={columns}
      rows={classGroups}
      getRowId={(classGroup) => classGroup.id}
      emptyMessage={t("classGroups.empty")}
      onEdit={onEdit}
      onDelete={onDelete}
    />
  );
}
