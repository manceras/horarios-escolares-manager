import type { QueryClient } from "@tanstack/react-query";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type Schedule = components["schemas"]["ScheduleRead"];
export type ScheduleDetail = components["schemas"]["ScheduleDetail"];
export type ScheduleCreate = components["schemas"]["ScheduleCreate"];
export type ScheduledSession = components["schemas"]["ScheduledSessionRead"];
export type ScheduledSessionUpdate = components["schemas"]["ScheduledSessionUpdate"];
export type GenerationResult = components["schemas"]["GenerationResult"];
export type ConflictReport = components["schemas"]["ConflictReport"];
export type Conflict = components["schemas"]["ConflictRead"];
export type TimeSlot = components["schemas"]["TimeSlotRead"];
export type ClassGroup = components["schemas"]["ClassGroupRead"];

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

export function useSchedule(scheduleId: number) {
  return useQuery({
    queryKey: queryKeys.schedules.detail(scheduleId),
    queryFn: async (): Promise<ScheduleDetail> => {
      const { data, error } = await api.GET("/api/v1/schedules/{schedule_id}", {
        params: { path: { schedule_id: scheduleId } },
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

export function useScheduleConflicts(scheduleId: number) {
  return useQuery({
    queryKey: queryKeys.schedules.conflicts(scheduleId),
    queryFn: async (): Promise<ConflictReport> => {
      const { data, error } = await api.GET("/api/v1/schedules/{schedule_id}/conflicts", {
        params: { path: { schedule_id: scheduleId } },
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

/** The empty week the grid is drawn on, break slots included. */
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

/** One grid column per class group. */
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

export function useCreateSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: ScheduleCreate): Promise<Schedule> => {
      const { data, error } = await api.POST("/api/v1/schedules", { body: payload });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "schedules.createSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.schedules.all });
    },
  });
}

export function useDeleteSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (scheduleId: number): Promise<void> => {
      const { error } = await api.DELETE("/api/v1/schedules/{schedule_id}", {
        params: { path: { schedule_id: scheduleId } },
      });
      if (error) throw new ApiRequestError(error);
    },
    meta: { successMessageKey: "schedules.deleteSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.schedules.all });
    },
  });
}

export function usePublishSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (scheduleId: number): Promise<Schedule> => {
      const { data, error } = await api.POST("/api/v1/schedules/{schedule_id}/publish", {
        params: { path: { schedule_id: scheduleId } },
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "schedules.publishSuccess" },
    onSuccess: (schedule) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.schedules.all });
      void queryClient.invalidateQueries({ queryKey: queryKeys.schedules.detail(schedule.id) });
    },
  });
}

/**
 * Runs the solver synchronously; it can take seconds. An infeasible run is a
 * successful response with `solved: false`, not an error, so the caller reads
 * the outcome from the returned `GenerationResult`.
 */
export function useGenerateSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (scheduleId: number): Promise<GenerationResult> => {
      const { data, error } = await api.POST("/api/v1/schedules/{schedule_id}/generate", {
        params: { path: { schedule_id: scheduleId } },
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    onSuccess: (result) => {
      invalidateSchedule(queryClient, result.schedule_id);
    },
  });
}

export interface MoveSessionVariables {
  scheduleId: number;
  sessionId: number;
  /** The whole slot, so the optimistic row carries its day, period and times. */
  targetTimeSlot: TimeSlot;
}

interface OptimisticContext {
  previous: ScheduleDetail | undefined;
}

/**
 * Moves a session to another time slot, optimistically so the grid reacts at
 * once. The server re-validates the whole timetable and answers 409 when the
 * move introduces a conflict; the snapshot taken here is put back in that
 * case, so a refused move never stays on screen.
 */
export function useMoveSession() {
  const queryClient = useQueryClient();

  return useMutation<ScheduledSession, unknown, MoveSessionVariables, OptimisticContext>({
    mutationFn: async ({ scheduleId, sessionId, targetTimeSlot }) => {
      const payload: ScheduledSessionUpdate = { time_slot_id: targetTimeSlot.id };
      const { data, error } = await api.PATCH(
        "/api/v1/schedules/{schedule_id}/sessions/{session_id}",
        { params: { path: { schedule_id: scheduleId, session_id: sessionId } }, body: payload },
      );
      if (error) throw new ApiRequestError(error);
      return data;
    },
    onMutate: async ({ scheduleId, sessionId, targetTimeSlot }) => {
      return await applyOptimisticSessionPatch(queryClient, scheduleId, sessionId, (session) => ({
        ...session,
        time_slot_id: targetTimeSlot.id,
        day_of_week: targetTimeSlot.day_of_week,
        period_index: targetTimeSlot.period_index,
        start_time: targetTimeSlot.start_time,
        end_time: targetTimeSlot.end_time,
      }));
    },
    onError: (_error, { scheduleId }, context) => {
      rollbackSchedule(queryClient, scheduleId, context);
    },
    onSettled: (_data, _error, { scheduleId }) => {
      invalidateSchedule(queryClient, scheduleId);
    },
  });
}

export interface SetSessionLockVariables {
  scheduleId: number;
  sessionId: number;
  locked: boolean;
}

/** Pins a session so the next solver run has to preserve it, or releases it. */
export function useSetSessionLock() {
  const queryClient = useQueryClient();

  return useMutation<ScheduledSession, unknown, SetSessionLockVariables, OptimisticContext>({
    mutationFn: async ({ scheduleId, sessionId, locked }) => {
      const payload: ScheduledSessionUpdate = { locked };
      const { data, error } = await api.PATCH(
        "/api/v1/schedules/{schedule_id}/sessions/{session_id}",
        { params: { path: { schedule_id: scheduleId, session_id: sessionId } }, body: payload },
      );
      if (error) throw new ApiRequestError(error);
      return data;
    },
    onMutate: async ({ scheduleId, sessionId, locked }) => {
      return await applyOptimisticSessionPatch(queryClient, scheduleId, sessionId, (session) => ({
        ...session,
        locked,
      }));
    },
    onError: (_error, { scheduleId }, context) => {
      rollbackSchedule(queryClient, scheduleId, context);
    },
    onSettled: (_data, _error, { scheduleId }) => {
      invalidateSchedule(queryClient, scheduleId);
    },
  });
}

/** A write to a schedule changes both the grid and the conflicts it reports. */
function invalidateSchedule(queryClient: QueryClient, scheduleId: number): void {
  void queryClient.invalidateQueries({ queryKey: queryKeys.schedules.detail(scheduleId) });
  void queryClient.invalidateQueries({ queryKey: queryKeys.schedules.conflicts(scheduleId) });
  void queryClient.invalidateQueries({ queryKey: queryKeys.schedules.all });
}

async function applyOptimisticSessionPatch(
  queryClient: QueryClient,
  scheduleId: number,
  sessionId: number,
  patch: (session: ScheduledSession) => ScheduledSession,
): Promise<OptimisticContext> {
  const queryKey = queryKeys.schedules.detail(scheduleId);
  await queryClient.cancelQueries({ queryKey });

  const previous = queryClient.getQueryData<ScheduleDetail>(queryKey);
  if (previous !== undefined) {
    queryClient.setQueryData<ScheduleDetail>(queryKey, {
      ...previous,
      sessions: previous.sessions.map((session) =>
        session.id === sessionId ? patch(session) : session,
      ),
    });
  }

  return { previous };
}

function rollbackSchedule(
  queryClient: QueryClient,
  scheduleId: number,
  context: OptimisticContext | undefined,
): void {
  if (context?.previous !== undefined) {
    queryClient.setQueryData<ScheduleDetail>(
      queryKeys.schedules.detail(scheduleId),
      context.previous,
    );
  }
}
