import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type Subject = components["schemas"]["SubjectRead"];
export type SubjectCreate = components["schemas"]["SubjectCreate"];
export type SubjectUpdate = components["schemas"]["SubjectUpdate"];

export function useSubjects() {
  return useQuery({
    queryKey: queryKeys.subjects.all,
    queryFn: async (): Promise<Subject[]> => {
      const { data, error } = await api.GET("/api/v1/subjects");
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

export function useCreateSubject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: SubjectCreate): Promise<Subject> => {
      const { data, error } = await api.POST("/api/v1/subjects", { body: payload });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "subjects.createSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.subjects.all });
    },
  });
}

export function useUpdateSubject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: number;
      payload: SubjectUpdate;
    }): Promise<Subject> => {
      const { data, error } = await api.PATCH("/api/v1/subjects/{subject_id}", {
        params: { path: { subject_id: id } },
        body: payload,
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "subjects.updateSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.subjects.all });
    },
  });
}

export function useDeleteSubject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      const { error } = await api.DELETE("/api/v1/subjects/{subject_id}", {
        params: { path: { subject_id: id } },
      });
      if (error) throw new ApiRequestError(error);
    },
    meta: { successMessageKey: "subjects.deleteSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.subjects.all });
    },
  });
}
