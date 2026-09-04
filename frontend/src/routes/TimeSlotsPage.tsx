import type { SubmitEvent } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EntityDialog } from "@/components/EntityDialog";
import { QueryState } from "@/components/QueryState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TimeSlot, TimeSlotUpdate } from "@/features/time-slots/api";
import {
  useCreateTimeSlot,
  useDeleteTimeSlot,
  useTimeSlots,
  useUpdateTimeSlot,
} from "@/features/time-slots/api";
import { TimeSlotForm } from "@/features/time-slots/TimeSlotForm";
import { TimeSlotGrid } from "@/features/time-slots/TimeSlotGrid";
import {
  emptyTimeSlotFormValues,
  validateTimeSlotForm,
} from "@/features/time-slots/time-slot-form-values";
import type { TimeSlotFormValues } from "@/features/time-slots/time-slot-form-values";
import { formatTime } from "@/lib/time-format";
import { weekdayTranslationKey } from "@/lib/weekdays";
import { useEntityForm } from "@/lib/forms/useEntityForm";

function toTimeSlotFormValues(timeSlot: TimeSlot): TimeSlotFormValues {
  return {
    day_of_week: timeSlot.day_of_week,
    period_index: timeSlot.period_index,
    start_time: formatTime(timeSlot.start_time),
    end_time: formatTime(timeSlot.end_time),
    is_break: timeSlot.is_break,
  };
}

/** CRUD route for time slots, rendered as a weekly grid instead of a flat list. */
export function TimeSlotsPage() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useTimeSlots();

  const createTimeSlot = useCreateTimeSlot();
  const updateTimeSlot = useUpdateTimeSlot();
  const deleteTimeSlot = useDeleteTimeSlot();

  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingTimeSlot, setEditingTimeSlot] = useState<TimeSlot | null>(null);
  const [deletingTimeSlot, setDeletingTimeSlot] = useState<TimeSlot | null>(null);

  const createForm = useEntityForm(emptyTimeSlotFormValues, validateTimeSlotForm);
  const editForm = useEntityForm(emptyTimeSlotFormValues, validateTimeSlotForm);

  function openCreateDialog(): void {
    createForm.reset(emptyTimeSlotFormValues);
    createTimeSlot.reset();
    setCreateOpen(true);
  }

  function openEditDialog(timeSlot: TimeSlot): void {
    editForm.reset(toTimeSlotFormValues(timeSlot));
    updateTimeSlot.reset();
    setEditingTimeSlot(timeSlot);
  }

  function openDeleteDialog(timeSlot: TimeSlot): void {
    deleteTimeSlot.reset();
    setDeletingTimeSlot(timeSlot);
  }

  function handleCreateSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (!createForm.validate()) {
      return;
    }
    createTimeSlot.mutate(createForm.values, {
      onSuccess: () => {
        setCreateOpen(false);
      },
    });
  }

  function handleEditSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (editingTimeSlot === null || !editForm.validate()) {
      return;
    }
    const payload: TimeSlotUpdate = editForm.values;
    updateTimeSlot.mutate(
      { id: editingTimeSlot.id, payload },
      {
        onSuccess: () => {
          setEditingTimeSlot(null);
        },
      },
    );
  }

  function handleConfirmDelete(): void {
    if (deletingTimeSlot === null) {
      return;
    }
    deleteTimeSlot.mutate(deletingTimeSlot.id, {
      onSuccess: () => {
        setDeletingTimeSlot(null);
      },
    });
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{t("timeSlots.title")}</h1>
        <Button onClick={openCreateDialog}>{t("timeSlots.createButton")}</Button>
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
            <CardTitle>{t("timeSlots.title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <TimeSlotGrid timeSlots={data} onEdit={openEditDialog} onDelete={openDeleteDialog} />
          </CardContent>
        </Card>
      ) : null}

      <EntityDialog
        open={isCreateOpen}
        onOpenChange={setCreateOpen}
        title={t("timeSlots.createTitle")}
        onSubmit={handleCreateSubmit}
        isSubmitting={createTimeSlot.isPending}
        error={createTimeSlot.error}
      >
        <TimeSlotForm form={createForm} />
      </EntityDialog>

      <EntityDialog
        open={editingTimeSlot !== null}
        onOpenChange={(open) => {
          if (!open) {
            setEditingTimeSlot(null);
          }
        }}
        title={t("timeSlots.editTitle")}
        onSubmit={handleEditSubmit}
        isSubmitting={updateTimeSlot.isPending}
        error={updateTimeSlot.error}
      >
        <TimeSlotForm form={editForm} />
      </EntityDialog>

      <ConfirmDialog
        open={deletingTimeSlot !== null}
        onOpenChange={(open) => {
          if (!open) {
            setDeletingTimeSlot(null);
          }
        }}
        title={t("timeSlots.deleteTitle")}
        description={
          deletingTimeSlot
            ? t("timeSlots.deleteConfirm", {
                day: t(weekdayTranslationKey(deletingTimeSlot.day_of_week)),
                period: deletingTimeSlot.period_index + 1,
              })
            : undefined
        }
        onConfirm={handleConfirmDelete}
        isConfirming={deleteTimeSlot.isPending}
        error={deleteTimeSlot.error}
      />
    </section>
  );
}
