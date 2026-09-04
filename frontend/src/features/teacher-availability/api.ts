import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type TeacherUnavailability = components["schemas"]["TeacherUnavailabilityRead"];

export function useTeacherUnavailabilities(teacherId: number) {
  return useQuery({
    queryKey: queryKeys.teacherUnavailabilities.byTeacher(teacherId),
    queryFn: async (): Promise<TeacherUnavailability[]> => {
      const { data, error } = await api.GET("/api/v1/teacher-unavailabilities", {
        params: { query: { teacher_id: teacherId } },
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

/**
 * Replaces a teacher's whole set of blocked slots in one call, so toggling a
 * grid of checkboxes never fires one request per checkbox.
 */
export function useReplaceTeacherUnavailabilities(teacherId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (timeSlotIds: readonly number[]): Promise<TeacherUnavailability[]> => {
      const { data, error } = await api.PUT(
        "/api/v1/teacher-unavailabilities/teacher/{teacher_id}",
        {
          params: { path: { teacher_id: teacherId } },
          body: { time_slot_ids: [...timeSlotIds] },
        },
      );
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "availability.saveSuccess" },
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.teacherUnavailabilities.byTeacher(teacherId), data);
    },
  });
}
