import type { SubmitEvent } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EntityDialog } from "@/components/EntityDialog";
import { QueryState } from "@/components/QueryState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Subject, SubjectUpdate } from "@/features/subjects/api";
import {
  useCreateSubject,
  useDeleteSubject,
  useSubjects,
  useUpdateSubject,
} from "@/features/subjects/api";
import { SubjectForm } from "@/features/subjects/SubjectForm";
import {
  emptySubjectFormValues,
  validateSubjectForm,
} from "@/features/subjects/subject-form-values";
import type { SubjectFormValues } from "@/features/subjects/subject-form-values";
import { SubjectTable } from "@/features/subjects/SubjectTable";
import { useEntityForm } from "@/lib/forms/useEntityForm";

function toSubjectFormValues(subject: Subject): SubjectFormValues {
  return {
    code: subject.code,
    name: subject.name,
    required_room_type: subject.required_room_type ?? null,
  };
}

/** Composition only: data comes from feature hooks, states are delegated to shared components. */
export function SubjectsPage() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useSubjects();

  const createSubject = useCreateSubject();
  const updateSubject = useUpdateSubject();
  const deleteSubject = useDeleteSubject();

  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null);
  const [deletingSubject, setDeletingSubject] = useState<Subject | null>(null);

  const createForm = useEntityForm(emptySubjectFormValues, validateSubjectForm);
  const editForm = useEntityForm(emptySubjectFormValues, validateSubjectForm);

  function openCreateDialog(): void {
    createForm.reset(emptySubjectFormValues);
    createSubject.reset();
    setCreateOpen(true);
  }

  function openEditDialog(subject: Subject): void {
    editForm.reset(toSubjectFormValues(subject));
    updateSubject.reset();
    setEditingSubject(subject);
  }

  function openDeleteDialog(subject: Subject): void {
    deleteSubject.reset();
    setDeletingSubject(subject);
  }

  function handleCreateSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (!createForm.validate()) {
      return;
    }
    createSubject.mutate(createForm.values, {
      onSuccess: () => {
        setCreateOpen(false);
      },
    });
  }

  function handleEditSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (editingSubject === null || !editForm.validate()) {
      return;
    }
    const payload: SubjectUpdate = editForm.values;
    updateSubject.mutate(
      { id: editingSubject.id, payload },
      {
        onSuccess: () => {
          setEditingSubject(null);
        },
      },
    );
  }

  function handleConfirmDelete(): void {
    if (deletingSubject === null) {
      return;
    }
    deleteSubject.mutate(deletingSubject.id, {
      onSuccess: () => {
        setDeletingSubject(null);
      },
    });
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{t("subjects.title")}</h1>
        <Button onClick={openCreateDialog}>{t("subjects.createButton")}</Button>
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
            <CardTitle>{t("subjects.title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <SubjectTable subjects={data} onEdit={openEditDialog} onDelete={openDeleteDialog} />
          </CardContent>
        </Card>
      ) : null}

      <EntityDialog
        open={isCreateOpen}
        onOpenChange={setCreateOpen}
        title={t("subjects.createTitle")}
        onSubmit={handleCreateSubmit}
        isSubmitting={createSubject.isPending}
        error={createSubject.error}
      >
        <SubjectForm form={createForm} />
      </EntityDialog>

      <EntityDialog
        open={editingSubject !== null}
        onOpenChange={(open) => {
          if (!open) {
            setEditingSubject(null);
          }
        }}
        title={t("subjects.editTitle")}
        onSubmit={handleEditSubmit}
        isSubmitting={updateSubject.isPending}
        error={updateSubject.error}
      >
        <SubjectForm form={editForm} />
      </EntityDialog>

      <ConfirmDialog
        open={deletingSubject !== null}
        onOpenChange={(open) => {
          if (!open) {
            setDeletingSubject(null);
          }
        }}
        title={t("subjects.deleteTitle")}
        description={
          deletingSubject ? t("subjects.deleteConfirm", { name: deletingSubject.name }) : undefined
        }
        onConfirm={handleConfirmDelete}
        isConfirming={deleteSubject.isPending}
        error={deleteSubject.error}
      />
    </section>
  );
}
