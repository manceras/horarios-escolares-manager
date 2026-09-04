import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type Teacher = components["schemas"]["TeacherRead"];
export type TeacherCreate = components["schemas"]["TeacherCreate"];
export type TeacherUpdate = components["schemas"]["TeacherUpdate"];

/**
 * Reference data-access module: one file per feature, one hook per operation,
 * keys from `queryKeys`, invalidation right next to the mutation.
 */
export function useTeachers() {
  return useQuery({
    queryKey: queryKeys.teachers.all,
    queryFn: async (): Promise<Teacher[]> => {
      const { data, error } = await api.GET("/api/v1/teachers");
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

export function useCreateTeacher() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: TeacherCreate): Promise<Teacher> => {
      const { data, error } = await api.POST("/api/v1/teachers", { body: payload });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "teachers.createSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.teachers.all });
    },
  });
}

export function useUpdateTeacher() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: number;
      payload: TeacherUpdate;
    }): Promise<Teacher> => {
      const { data, error } = await api.PATCH("/api/v1/teachers/{teacher_id}", {
        params: { path: { teacher_id: id } },
        body: payload,
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "teachers.updateSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.teachers.all });
    },
  });
}

export function useDeleteTeacher() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      const { error } = await api.DELETE("/api/v1/teachers/{teacher_id}", {
        params: { path: { teacher_id: id } },
      });
      if (error) throw new ApiRequestError(error);
    },
    meta: { successMessageKey: "teachers.deleteSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.teachers.all });
    },
  });
}
