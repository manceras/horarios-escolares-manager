import type { SubmitEvent } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EntityDialog } from "@/components/EntityDialog";
import { QueryState } from "@/components/QueryState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Teacher, TeacherUpdate } from "@/features/teachers/api";
import {
  useCreateTeacher,
  useDeleteTeacher,
  useTeachers,
  useUpdateTeacher,
} from "@/features/teachers/api";
import { TeacherForm } from "@/features/teachers/TeacherForm";
import {
  emptyTeacherFormValues,
  validateTeacherForm,
} from "@/features/teachers/teacher-form-values";
import type { TeacherFormValues } from "@/features/teachers/teacher-form-values";
import { TeacherTable } from "@/features/teachers/TeacherTable";
import { useEntityForm } from "@/lib/forms/useEntityForm";

function toTeacherFormValues(teacher: Teacher): TeacherFormValues {
  return {
    first_name: teacher.first_name,
    last_name: teacher.last_name,
    email: teacher.email,
    is_specialist: teacher.is_specialist,
    max_periods_per_week: teacher.max_periods_per_week,
    active: teacher.active,
  };
}

/**
 * Reference route: composition only. Data comes from feature hooks, states
 * are delegated to shared components, and there is no business logic here.
 * Copy this file's shape for every other CRUD page.
 */
export function TeachersPage() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useTeachers();

  const createTeacher = useCreateTeacher();
  const updateTeacher = useUpdateTeacher();
  const deleteTeacher = useDeleteTeacher();

  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState<Teacher | null>(null);
  const [deletingTeacher, setDeletingTeacher] = useState<Teacher | null>(null);

  const createForm = useEntityForm(emptyTeacherFormValues, validateTeacherForm);
  const editForm = useEntityForm(emptyTeacherFormValues, validateTeacherForm);

  function openCreateDialog(): void {
    createForm.reset(emptyTeacherFormValues);
    createTeacher.reset();
    setCreateOpen(true);
  }

  function openEditDialog(teacher: Teacher): void {
    editForm.reset(toTeacherFormValues(teacher));
    updateTeacher.reset();
    setEditingTeacher(teacher);
  }

  function openDeleteDialog(teacher: Teacher): void {
    deleteTeacher.reset();
    setDeletingTeacher(teacher);
  }

  function handleCreateSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (!createForm.validate()) {
      return;
    }
    createTeacher.mutate(createForm.values, {
      onSuccess: () => {
        setCreateOpen(false);
      },
    });
  }

  function handleEditSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (editingTeacher === null || !editForm.validate()) {
      return;
    }
    const payload: TeacherUpdate = editForm.values;
    updateTeacher.mutate(
      { id: editingTeacher.id, payload },
      {
        onSuccess: () => {
          setEditingTeacher(null);
        },
      },
    );
  }

  function handleConfirmDelete(): void {
    if (deletingTeacher === null) {
      return;
    }
    deleteTeacher.mutate(deletingTeacher.id, {
      onSuccess: () => {
        setDeletingTeacher(null);
      },
    });
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{t("teachers.title")}</h1>
        <Button onClick={openCreateDialog}>{t("teachers.createButton")}</Button>
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
            <CardTitle>{t("teachers.title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <TeacherTable teachers={data} onEdit={openEditDialog} onDelete={openDeleteDialog} />
          </CardContent>
        </Card>
      ) : null}

      <EntityDialog
        open={isCreateOpen}
        onOpenChange={setCreateOpen}
        title={t("teachers.createTitle")}
        onSubmit={handleCreateSubmit}
        isSubmitting={createTeacher.isPending}
        error={createTeacher.error}
      >
        <TeacherForm form={createForm} />
      </EntityDialog>

      <EntityDialog
        open={editingTeacher !== null}
        onOpenChange={(open) => {
          if (!open) {
            setEditingTeacher(null);
          }
        }}
        title={t("teachers.editTitle")}
        onSubmit={handleEditSubmit}
        isSubmitting={updateTeacher.isPending}
        error={updateTeacher.error}
      >
        <TeacherForm form={editForm} />
      </EntityDialog>

      <ConfirmDialog
        open={deletingTeacher !== null}
        onOpenChange={(open) => {
          if (!open) {
            setDeletingTeacher(null);
          }
        }}
        title={t("teachers.deleteTitle")}
        description={
          deletingTeacher
            ? t("teachers.deleteConfirm", {
                name: `${deletingTeacher.first_name} ${deletingTeacher.last_name}`,
              })
            : undefined
        }
        onConfirm={handleConfirmDelete}
        isConfirming={deleteTeacher.isPending}
        error={deleteTeacher.error}
      />
    </section>
  );
}
