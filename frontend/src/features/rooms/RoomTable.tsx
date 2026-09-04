import { useTranslation } from "react-i18next";

import { DataTable, type DataTableColumn } from "@/components/DataTable";

import type { Room } from "./api";

interface RoomTableProps {
  rooms: readonly Room[];
  onEdit: (room: Room) => void;
  onDelete: (room: Room) => void;
}

export function RoomTable({ rooms, onEdit, onDelete }: RoomTableProps) {
  const { t } = useTranslation();

  const columns: DataTableColumn<Room>[] = [
    { key: "name", header: t("rooms.name"), cell: (room) => room.name },
    {
      key: "type",
      header: t("rooms.type"),
      cell: (room) => t(`rooms.types.${room.room_type}`),
    },
    { key: "capacity", header: t("rooms.capacity"), cell: (room) => room.capacity },
  ];

  return (
    <DataTable
      columns={columns}
      rows={rooms}
      getRowId={(room) => room.id}
      emptyMessage={t("rooms.empty")}
      onEdit={onEdit}
      onDelete={onDelete}
    />
  );
}
