import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { QueryClient } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type CurriculumEntry = components["schemas"]["CurriculumEntryDetail"];
export type CurriculumEntryCreate = components["schemas"]["CurriculumEntryCreate"];
export type CurriculumEntryUpdate = components["schemas"]["CurriculumEntryUpdate"];
export type WorkloadReport = components["schemas"]["WorkloadReport"];
export type GroupWorkload = components["schemas"]["GroupWorkload"];
export type TeacherWorkload = components["schemas"]["TeacherWorkload"];
export type ClassGroup = components["schemas"]["ClassGroupRead"];
export type Subject = components["schemas"]["SubjectRead"];

/**
 * Data-access module for the curriculum screen. It also exposes read-only
 * lookups for class groups and subjects, needed to populate the entry form's
 * selects -- `features/class-groups/` and `features/subjects/` are owned by
 * other work and are not touched here.
 */
export function useCurriculumEntries() {
  return useQuery({
    queryKey: queryKeys.curriculumEntries.all,
    queryFn: async (): Promise<CurriculumEntry[]> => {
      const { data, error } = await api.GET("/api/v1/curriculum-entries");
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

export function useWorkload() {
  return useQuery({
    queryKey: queryKeys.curriculumEntries.workload,
    queryFn: async (): Promise<WorkloadReport> => {
      const { data, error } = await api.GET("/api/v1/curriculum-entries/workload");
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

export function useClassGroups() {
  return useQuery({
    queryKey: queryKeys.classGroups.all,
    queryFn: async (): Promise<ClassGroup[]> => {
      const { data, error } = await api.GET("/api/v1/class-groups");
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

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

/**
 * Creating, updating or deleting an entry can flip a class group or a
 * teacher between fitting and not fitting, so every mutation refreshes both
 * the entry list and the workload report.
 */
function invalidateCurriculum(queryClient: QueryClient): void {
  void queryClient.invalidateQueries({ queryKey: queryKeys.curriculumEntries.all });
  void queryClient.invalidateQueries({ queryKey: queryKeys.curriculumEntries.workload });
}

export function useCreateCurriculumEntry() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: CurriculumEntryCreate) => {
      const { data, error } = await api.POST("/api/v1/curriculum-entries", { body: payload });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "curriculum.createSuccess" },
    onSuccess: () => {
      invalidateCurriculum(queryClient);
    },
  });
}

export function useUpdateCurriculumEntry() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: CurriculumEntryUpdate }) => {
      const { data, error } = await api.PATCH("/api/v1/curriculum-entries/{entry_id}", {
        params: { path: { entry_id: id } },
        body: payload,
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "curriculum.updateSuccess" },
    onSuccess: () => {
      invalidateCurriculum(queryClient);
    },
  });
}

export function useDeleteCurriculumEntry() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      const { error } = await api.DELETE("/api/v1/curriculum-entries/{entry_id}", {
        params: { path: { entry_id: id } },
      });
      if (error) throw new ApiRequestError(error);
    },
    meta: { successMessageKey: "curriculum.deleteSuccess" },
    onSuccess: () => {
      invalidateCurriculum(queryClient);
    },
  });
}
