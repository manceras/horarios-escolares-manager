import type { SubmitEvent } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EntityDialog } from "@/components/EntityDialog";
import { QueryState } from "@/components/QueryState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ClassGroup, ClassGroupUpdate } from "@/features/class-groups/api";
import {
  useClassGroups,
  useCreateClassGroup,
  useDeleteClassGroup,
  useUpdateClassGroup,
} from "@/features/class-groups/api";
import { ClassGroupForm } from "@/features/class-groups/ClassGroupForm";
import {
  emptyClassGroupFormValues,
  validateClassGroupForm,
} from "@/features/class-groups/class-group-form-values";
import type { ClassGroupFormValues } from "@/features/class-groups/class-group-form-values";
import { ClassGroupTable } from "@/features/class-groups/ClassGroupTable";
import { useEntityForm } from "@/lib/forms/useEntityForm";

function toClassGroupFormValues(classGroup: ClassGroup): ClassGroupFormValues {
  return {
    name: classGroup.name,
    grade: classGroup.grade,
    tutor_id: classGroup.tutor_id ?? null,
    home_room_id: classGroup.home_room_id ?? null,
  };
}

/**
 * CRUD route for class groups. Composition only, following the pattern set
 * by `TeachersPage`: data from feature hooks, states delegated to shared
 * components.
 */
export function ClassGroupsPage() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useClassGroups();

  const createClassGroup = useCreateClassGroup();
  const updateClassGroup = useUpdateClassGroup();
  const deleteClassGroup = useDeleteClassGroup();

  const [isCreateOpen, setCreateOpen] = useState(false);
  const [editingClassGroup, setEditingClassGroup] = useState<ClassGroup | null>(null);
  const [deletingClassGroup, setDeletingClassGroup] = useState<ClassGroup | null>(null);

  const createForm = useEntityForm(emptyClassGroupFormValues, validateClassGroupForm);
  const editForm = useEntityForm(emptyClassGroupFormValues, validateClassGroupForm);

  function openCreateDialog(): void {
    createForm.reset(emptyClassGroupFormValues);
    createClassGroup.reset();
    setCreateOpen(true);
  }

  function openEditDialog(classGroup: ClassGroup): void {
    editForm.reset(toClassGroupFormValues(classGroup));
    updateClassGroup.reset();
    setEditingClassGroup(classGroup);
  }

  function openDeleteDialog(classGroup: ClassGroup): void {
    deleteClassGroup.reset();
    setDeletingClassGroup(classGroup);
  }

  function handleCreateSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (!createForm.validate()) {
      return;
    }
    createClassGroup.mutate(createForm.values, {
      onSuccess: () => {
        setCreateOpen(false);
      },
    });
  }

  function handleEditSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (editingClassGroup === null || !editForm.validate()) {
      return;
    }
    const payload: ClassGroupUpdate = editForm.values;
    updateClassGroup.mutate(
      { id: editingClassGroup.id, payload },
      {
        onSuccess: () => {
          setEditingClassGroup(null);
        },
      },
    );
  }

  function handleConfirmDelete(): void {
    if (deletingClassGroup === null) {
      return;
    }
    deleteClassGroup.mutate(deletingClassGroup.id, {
      onSuccess: () => {
        setDeletingClassGroup(null);
      },
    });
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{t("classGroups.title")}</h1>
        <Button onClick={openCreateDialog}>{t("classGroups.createButton")}</Button>
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
            <CardTitle>{t("classGroups.title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <ClassGroupTable
              classGroups={data}
              onEdit={openEditDialog}
              onDelete={openDeleteDialog}
            />
          </CardContent>
        </Card>
      ) : null}

      <EntityDialog
        open={isCreateOpen}
        onOpenChange={setCreateOpen}
        title={t("classGroups.createTitle")}
        onSubmit={handleCreateSubmit}
        isSubmitting={createClassGroup.isPending}
        error={createClassGroup.error}
      >
        <ClassGroupForm form={createForm} />
      </EntityDialog>

      <EntityDialog
        open={editingClassGroup !== null}
        onOpenChange={(open) => {
          if (!open) {
            setEditingClassGroup(null);
          }
        }}
        title={t("classGroups.editTitle")}
        onSubmit={handleEditSubmit}
        isSubmitting={updateClassGroup.isPending}
        error={updateClassGroup.error}
      >
        <ClassGroupForm form={editForm} />
      </EntityDialog>

      <ConfirmDialog
        open={deletingClassGroup !== null}
        onOpenChange={(open) => {
          if (!open) {
            setDeletingClassGroup(null);
          }
        }}
        title={t("classGroups.deleteTitle")}
        description={
          deletingClassGroup
            ? t("classGroups.deleteConfirm", { name: deletingClassGroup.name })
            : undefined
        }
        onConfirm={handleConfirmDelete}
        isConfirming={deleteClassGroup.isPending}
        error={deleteClassGroup.error}
      />
    </section>
  );
}
