import { useQuery } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type Schedule = components["schemas"]["ScheduleRead"];
export type ScheduleDetail = components["schemas"]["ScheduleDetail"];
export type ScheduledSession = components["schemas"]["ScheduledSessionRead"];
export type TimeSlot = components["schemas"]["TimeSlotRead"];

/**
 * Data-access module for the printable/exportable schedule views. Kept
 * separate from `features/schedules/` (owned by another agent) even though
 * both read the same endpoints -- a little duplication beats a shared file
 * edited by two agents at once.
 */
export function useSchedules() {
  return useQuery({
    queryKey: queryKeys.schedules.all,
    queryFn: async (): Promise<Schedule[]> => {
      const { data, error } = await api.GET("/api/v1/schedules");
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

export function useScheduleDetail(scheduleId: number | undefined) {
  return useQuery({
    queryKey: queryKeys.schedules.detail(scheduleId ?? -1),
    enabled: scheduleId !== undefined,
    queryFn: async (): Promise<ScheduleDetail> => {
      if (scheduleId === undefined) {
        throw new Error("useScheduleDetail called without a schedule id");
      }
      const { data, error } = await api.GET("/api/v1/schedules/{schedule_id}", {
        params: { path: { schedule_id: scheduleId } },
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

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
