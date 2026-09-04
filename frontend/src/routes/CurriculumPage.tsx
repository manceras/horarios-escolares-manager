import type { SubmitEvent } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EntityDialog } from "@/components/EntityDialog";
import { QueryState } from "@/components/QueryState";
import { Button } from "@/components/ui/button";
import type {
  CurriculumEntry,
  CurriculumEntryCreate,
  CurriculumEntryUpdate,
} from "@/features/curriculum/api";
import {
  useClassGroups,
  useCreateCurriculumEntry,
  useCurriculumEntries,
  useDeleteCurriculumEntry,
  useSubjects,
  useUpdateCurriculumEntry,
} from "@/features/curriculum/api";
import { CurriculumForm } from "@/features/curriculum/CurriculumForm";
import {
  emptyCurriculumFormValues,
  validateCurriculumForm,
} from "@/features/curriculum/curriculum-form-values";
import type { CurriculumFormValues } from "@/features/curriculum/curriculum-form-values";
import { CurriculumTable } from "@/features/curriculum/CurriculumTable";
import { WorkloadPanel } from "@/features/curriculum/WorkloadPanel";
import { useTeachers } from "@/features/teachers/api";
import { useEntityForm } from "@/lib/forms/useEntityForm";

function toCurriculumFormValues(entry: CurriculumEntry): CurriculumFormValues {
  return {
    class_group_id: entry.class_group_id,
    subject_id: entry.subject_id,
    teacher_id: entry.teacher_id,
    periods_per_week: entry.periods_per_week,
  };
}

/**
 * The solver's input: what each class group studies, with whom and how
 * often. The workload report sits above the table because it is the point
 * of this screen -- it tells the head of studies whether a timetable is even
 * possible before they generate one.
 */
export function CurriculumPage() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useCurriculumEntries();
  const classGroupsQuery = useClassGroups();
  const subjectsQuery = useSubjects();
  const teachersQuery = useTeachers();

  const createEntry = useCreateCurriculumEntry();
  const updateEntry = useUpdateCurriculumEntry();
  const deleteEntry = useDeleteCurriculumEntry();

  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState<CurriculumEntry | null>(null);
  const [deletingEntry, setDeletingEntry] = useState<CurriculumEntry | null>(null);

  const createForm = useEntityForm(emptyCurriculumFormValues, validateCurriculumForm);
  const editForm = useEntityForm(emptyCurriculumFormValues, validateCurriculumForm);

  const classGroups = classGroupsQuery.data ?? [];
  const subjects = subjectsQuery.data ?? [];
  const teachers = teachersQuery.data ?? [];

  const isOptionsLoading =
    classGroupsQuery.isLoading || subjectsQuery.isLoading || teachersQuery.isLoading;
  const optionsError = classGroupsQuery.error ?? subjectsQuery.error ?? teachersQuery.error;

  function retryEverything(): void {
    void refetch();
    void classGroupsQuery.refetch();
    void subjectsQuery.refetch();
    void teachersQuery.refetch();
  }

  function openCreateDialog(): void {
    createForm.reset(emptyCurriculumFormValues);
    createEntry.reset();
    setCreateOpen(true);
  }

  function openEditDialog(entry: CurriculumEntry): void {
    editForm.reset(toCurriculumFormValues(entry));
    updateEntry.reset();
    setEditingEntry(entry);
  }

  function openDeleteDialog(entry: CurriculumEntry): void {
    deleteEntry.reset();
    setDeletingEntry(entry);
  }

  function handleCreateSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (!createForm.validate()) {
      return;
    }
    const payload: CurriculumEntryCreate = createForm.values;
    createEntry.mutate(payload, {
      onSuccess: () => {
        setCreateOpen(false);
      },
    });
  }

  function handleEditSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (editingEntry === null || !editForm.validate()) {
      return;
    }
    const payload: CurriculumEntryUpdate = editForm.values;
    updateEntry.mutate(
      { id: editingEntry.id, payload },
      {
        onSuccess: () => {
          setEditingEntry(null);
        },
      },
    );
  }

  function handleConfirmDelete(): void {
    if (deletingEntry === null) {
      return;
    }
    deleteEntry.mutate(deletingEntry.id, {
      onSuccess: () => {
        setDeletingEntry(null);
      },
    });
  }

  return (
    <section className="space-y-6">
      <WorkloadPanel />

      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{t("curriculum.title")}</h1>
        <Button onClick={openCreateDialog} disabled={isOptionsLoading}>
          {t("curriculum.createButton")}
        </Button>
      </div>

      <QueryState
        isLoading={isLoading || isOptionsLoading}
        error={error ?? optionsError}
        onRetry={retryEverything}
      />

      {data ? (
        <CurriculumTable entries={data} onEdit={openEditDialog} onDelete={openDeleteDialog} />
      ) : null}

      <EntityDialog
        open={isCreateOpen}
        onOpenChange={setCreateOpen}
        title={t("curriculum.createTitle")}
        onSubmit={handleCreateSubmit}
        isSubmitting={createEntry.isPending}
        error={createEntry.error}
      >
        <CurriculumForm
          form={createForm}
          classGroups={classGroups}
          subjects={subjects}
          teachers={teachers}
          submitError={createEntry.error}
        />
      </EntityDialog>

      <EntityDialog
        open={editingEntry !== null}
        onOpenChange={(open) => {
          if (!open) {
            setEditingEntry(null);
          }
        }}
        title={t("curriculum.editTitle")}
        onSubmit={handleEditSubmit}
        isSubmitting={updateEntry.isPending}
        error={updateEntry.error}
      >
        <CurriculumForm
          form={editForm}
          classGroups={classGroups}
          subjects={subjects}
          teachers={teachers}
          submitError={updateEntry.error}
        />
      </EntityDialog>

      <ConfirmDialog
        open={deletingEntry !== null}
        onOpenChange={(open) => {
          if (!open) {
            setDeletingEntry(null);
          }
        }}
        title={t("curriculum.deleteTitle")}
        description={
          deletingEntry
            ? t("curriculum.deleteConfirm", {
                classGroup: deletingEntry.class_group_name,
                subject: deletingEntry.subject_name,
              })
            : undefined
        }
        onConfirm={handleConfirmDelete}
        isConfirming={deleteEntry.isPending}
        error={deleteEntry.error}
      />
    </section>
  );
}
