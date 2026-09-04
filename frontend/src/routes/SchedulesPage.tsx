import type { SubmitEvent } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EntityDialog } from "@/components/EntityDialog";
import { QueryState } from "@/components/QueryState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Schedule } from "@/features/schedules/api";
import {
  useCreateSchedule,
  useDeleteSchedule,
  usePublishSchedule,
  useSchedules,
} from "@/features/schedules/api";
import { ScheduleForm } from "@/features/schedules/ScheduleForm";
import {
  emptyScheduleFormValues,
  validateScheduleForm,
} from "@/features/schedules/schedule-form-values";
import { ScheduleTable } from "@/features/schedules/ScheduleTable";
import { useEntityForm } from "@/lib/forms/useEntityForm";

/** The timetable versions of the school: create a draft, publish one, delete one. */
export function SchedulesPage() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useSchedules();

  const createSchedule = useCreateSchedule();
  const deleteSchedule = useDeleteSchedule();
  const publishSchedule = usePublishSchedule();

  const [isCreateOpen, setCreateOpen] = useState(false);
  const [deletingSchedule, setDeletingSchedule] = useState<Schedule | null>(null);
  const [publishingSchedule, setPublishingSchedule] = useState<Schedule | null>(null);

  const createForm = useEntityForm(emptyScheduleFormValues, validateScheduleForm);

  function openCreateDialog(): void {
    createForm.reset(emptyScheduleFormValues);
    createSchedule.reset();
    setCreateOpen(true);
  }

  function handleCreateSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (!createForm.validate()) {
      return;
    }
    createSchedule.mutate(createForm.values, {
      onSuccess: () => {
        setCreateOpen(false);
      },
    });
  }

  function handleConfirmDelete(): void {
    if (deletingSchedule === null) {
      return;
    }
    deleteSchedule.mutate(deletingSchedule.id, {
      onSuccess: () => {
        setDeletingSchedule(null);
      },
    });
  }

  function handleConfirmPublish(): void {
    if (publishingSchedule === null) {
      return;
    }
    publishSchedule.mutate(publishingSchedule.id, {
      onSuccess: () => {
        setPublishingSchedule(null);
      },
    });
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{t("schedules.title")}</h1>
        <Button onClick={openCreateDialog}>{t("schedules.createButton")}</Button>
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
            <CardTitle>{t("schedules.title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <ScheduleTable
              schedules={data}
              onPublish={(schedule) => {
                publishSchedule.reset();
                setPublishingSchedule(schedule);
              }}
              onDelete={(schedule) => {
                deleteSchedule.reset();
                setDeletingSchedule(schedule);
              }}
            />
          </CardContent>
        </Card>
      ) : null}

      <EntityDialog
        open={isCreateOpen}
        onOpenChange={setCreateOpen}
        title={t("schedules.createTitle")}
        onSubmit={handleCreateSubmit}
        isSubmitting={createSchedule.isPending}
        error={createSchedule.error}
      >
        <ScheduleForm form={createForm} />
      </EntityDialog>

      <ConfirmDialog
        open={deletingSchedule !== null}
        onOpenChange={(open) => {
          if (!open) {
            setDeletingSchedule(null);
          }
        }}
        title={t("schedules.deleteTitle")}
        description={
          deletingSchedule
            ? t("schedules.deleteConfirm", { name: deletingSchedule.name })
            : undefined
        }
        onConfirm={handleConfirmDelete}
        isConfirming={deleteSchedule.isPending}
        error={deleteSchedule.error}
      />

      <ConfirmDialog
        open={publishingSchedule !== null}
        onOpenChange={(open) => {
          if (!open) {
            setPublishingSchedule(null);
          }
        }}
        title={t("schedules.publishTitle")}
        description={
          publishingSchedule
            ? t("schedules.publishConfirm", { name: publishingSchedule.name })
            : undefined
        }
        onConfirm={handleConfirmPublish}
        isConfirming={publishSchedule.isPending}
        error={publishSchedule.error}
        confirmLabel={t("schedules.publish")}
      />
    </section>
  );
}
