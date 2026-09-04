import type { SubmitEvent } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EntityDialog } from "@/components/EntityDialog";
import { QueryState } from "@/components/QueryState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Room, RoomUpdate } from "@/features/rooms/api";
import { useCreateRoom, useDeleteRoom, useRooms, useUpdateRoom } from "@/features/rooms/api";
import { RoomForm } from "@/features/rooms/RoomForm";
import { emptyRoomFormValues, validateRoomForm } from "@/features/rooms/room-form-values";
import type { RoomFormValues } from "@/features/rooms/room-form-values";
import { RoomTable } from "@/features/rooms/RoomTable";
import { useEntityForm } from "@/lib/forms/useEntityForm";

function toRoomFormValues(room: Room): RoomFormValues {
  return {
    name: room.name,
    room_type: room.room_type,
    capacity: room.capacity,
  };
}

/** Composition only: data comes from feature hooks, states are delegated to shared components. */
export function RoomsPage() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useRooms();

  const createRoom = useCreateRoom();
  const updateRoom = useUpdateRoom();
  const deleteRoom = useDeleteRoom();

  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [deletingRoom, setDeletingRoom] = useState<Room | null>(null);

  const createForm = useEntityForm(emptyRoomFormValues, validateRoomForm);
  const editForm = useEntityForm(emptyRoomFormValues, validateRoomForm);

  function openCreateDialog(): void {
    createForm.reset(emptyRoomFormValues);
    createRoom.reset();
    setCreateOpen(true);
  }

  function openEditDialog(room: Room): void {
    editForm.reset(toRoomFormValues(room));
    updateRoom.reset();
    setEditingRoom(room);
  }

  function openDeleteDialog(room: Room): void {
    deleteRoom.reset();
    setDeletingRoom(room);
  }

  function handleCreateSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (!createForm.validate()) {
      return;
    }
    createRoom.mutate(createForm.values, {
      onSuccess: () => {
        setCreateOpen(false);
      },
    });
  }

  function handleEditSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (editingRoom === null || !editForm.validate()) {
      return;
    }
    const payload: RoomUpdate = editForm.values;
    updateRoom.mutate(
      { id: editingRoom.id, payload },
      {
        onSuccess: () => {
          setEditingRoom(null);
        },
      },
    );
  }

  function handleConfirmDelete(): void {
    if (deletingRoom === null) {
      return;
    }
    deleteRoom.mutate(deletingRoom.id, {
      onSuccess: () => {
        setDeletingRoom(null);
      },
    });
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{t("rooms.title")}</h1>
        <Button onClick={openCreateDialog}>{t("rooms.createButton")}</Button>
      </div>

      <QueryState
        isLoading={isLoading}
        error={error}
        onRetry={() => {
          void refetch();
        }}
      />

      {data ? (
        <Card>
          <CardHeader>
            <CardTitle>{t("rooms.title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <RoomTable rooms={data} onEdit={openEditDialog} onDelete={openDeleteDialog} />
          </CardContent>
        </Card>
      ) : null}

      <EntityDialog
        open={isCreateOpen}
        onOpenChange={setCreateOpen}
        title={t("rooms.createTitle")}
        onSubmit={handleCreateSubmit}
        isSubmitting={createRoom.isPending}
        error={createRoom.error}
      >
        <RoomForm form={createForm} />
      </EntityDialog>

      <EntityDialog
        open={editingRoom !== null}
        onOpenChange={(open) => {
          if (!open) {
            setEditingRoom(null);
          }
        }}
        title={t("rooms.editTitle")}
        onSubmit={handleEditSubmit}
        isSubmitting={updateRoom.isPending}
        error={updateRoom.error}
      >
        <RoomForm form={editForm} />
      </EntityDialog>

      <ConfirmDialog
        open={deletingRoom !== null}
        onOpenChange={(open) => {
          if (!open) {
            setDeletingRoom(null);
          }
        }}
        title={t("rooms.deleteTitle")}
        description={
          deletingRoom ? t("rooms.deleteConfirm", { name: deletingRoom.name }) : undefined
        }
        onConfirm={handleConfirmDelete}
        isConfirming={deleteRoom.isPending}
        error={deleteRoom.error}
      />
    </section>
  );
}
