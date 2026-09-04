import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type TimeSlot = components["schemas"]["TimeSlotRead"];
export type TimeSlotCreate = components["schemas"]["TimeSlotCreate"];
export type TimeSlotUpdate = components["schemas"]["TimeSlotUpdate"];

export function useTimeSlots() {
  return useQuery({
    queryKey: queryKeys.timeSlots.all,
    queryFn: async (): Promise<TimeSlot[]> => {
      const { data, error } = await api.GET("/api/v1/time-slots");
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

export function useCreateTimeSlot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: TimeSlotCreate): Promise<TimeSlot> => {
      const { data, error } = await api.POST("/api/v1/time-slots", { body: payload });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "timeSlots.createSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.timeSlots.all });
    },
  });
}

export function useUpdateTimeSlot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: number;
      payload: TimeSlotUpdate;
    }): Promise<TimeSlot> => {
      const { data, error } = await api.PATCH("/api/v1/time-slots/{time_slot_id}", {
        params: { path: { time_slot_id: id } },
        body: payload,
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "timeSlots.updateSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.timeSlots.all });
    },
  });
}

export function useDeleteTimeSlot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      const { error } = await api.DELETE("/api/v1/time-slots/{time_slot_id}", {
        params: { path: { time_slot_id: id } },
      });
      if (error) throw new ApiRequestError(error);
    },
    meta: { successMessageKey: "timeSlots.deleteSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.timeSlots.all });
    },
  });
}
