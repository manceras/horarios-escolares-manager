import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type Room = components["schemas"]["RoomRead"];
export type RoomCreate = components["schemas"]["RoomCreate"];
export type RoomUpdate = components["schemas"]["RoomUpdate"];
export type RoomType = components["schemas"]["RoomType"];

export function useRooms() {
  return useQuery({
    queryKey: queryKeys.rooms.all,
    queryFn: async (): Promise<Room[]> => {
      const { data, error } = await api.GET("/api/v1/rooms");
      if (error) throw new ApiRequestError(error);
      return data;
    },
  });
}

export function useCreateRoom() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: RoomCreate): Promise<Room> => {
      const { data, error } = await api.POST("/api/v1/rooms", { body: payload });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "rooms.createSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.rooms.all });
    },
  });
}

export function useUpdateRoom() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: RoomUpdate }): Promise<Room> => {
      const { data, error } = await api.PATCH("/api/v1/rooms/{room_id}", {
        params: { path: { room_id: id } },
        body: payload,
      });
      if (error) throw new ApiRequestError(error);
      return data;
    },
    meta: { successMessageKey: "rooms.updateSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.rooms.all });
    },
  });
}

export function useDeleteRoom() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      const { error } = await api.DELETE("/api/v1/rooms/{room_id}", {
        params: { path: { room_id: id } },
      });
      if (error) throw new ApiRequestError(error);
    },
    meta: { successMessageKey: "rooms.deleteSuccess" },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.rooms.all });
    },
  });
}
