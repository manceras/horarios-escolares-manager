import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type ClassGroup = components["schemas"]["ClassGroupRead"];
export type ClassGroupCreate = components["schemas"]["ClassGroupCreate"];
export type ClassGroupUpdate = components["schemas"]["ClassGroupUpdate"];
export type Room = components["schemas"]["RoomRead"];

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

/**
 * Rooms, fetched only to populate the `home_room_id` select. `features/rooms`
 * belongs to another agent, so this feature reads the endpoint directly
 * instead of depending on that module.
 */
export function useRoomOptions() {
  return useQuery({
    queryKey: queryKeys.rooms.all,
    queryFn: async (): Promise<Room[]> => {
      const { data, error } = await api.GET("/api/v1/rooms");
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

export function useCreateClassGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: ClassGroupCreate): Promise<ClassGroup> => {
      const { data, error } = await api.POST("/api/v1/class-groups", { body: payload });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "classGroups.createSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.classGroups.all });
    },
  });
}

export function useUpdateClassGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: number;
      payload: ClassGroupUpdate;
    }): Promise<ClassGroup> => {
      const { data, error } = await api.PATCH("/api/v1/class-groups/{class_group_id}", {
        params: { path: { class_group_id: id } },
        body: payload,
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "classGroups.updateSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.classGroups.all });
    },
  });
}

export function useDeleteClassGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      const { error } = await api.DELETE("/api/v1/class-groups/{class_group_id}", {
        params: { path: { class_group_id: id } },
      });
      if (error) throw new ApiRequestError(error);
    },
    meta: { successMessageKey: "classGroups.deleteSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.classGroups.all });
    },
  });
}
