import { useMutation, useQuery } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api/client";
import { queryKeys } from "@/lib/api/query-keys";
import type { components } from "@/lib/api/schema";

export type UpdateStatus = components["schemas"]["UpdateStatusRead"];

/** How long a check stays fresh. The answer changes at most once a release. */
const ONE_HOUR_IN_MS = 60 * 60 * 1000;

export function useUpdateStatus() {
  return useQuery({
    queryKey: queryKeys.updateStatus,
    queryFn: async (): Promise<UpdateStatus> => {
      const { data, error } = await api.GET("/api/v1/updates");
      if (error) throw new ApiRequestError(error);
      return data;
    },
    staleTime: ONE_HOUR_IN_MS,
    refetchOnWindowFocus: false,
    // A failed check is not worth a retry storm: the school simply stays on
    // the version they have, and the banner never appears.
    retry: false,
  });
}

export function useInstallUpdate() {
  return useMutation({
    mutationFn: async (): Promise<void> => {
      const { error } = await api.POST("/api/v1/updates/install");
      if (error) throw new ApiRequestError(error);
    },
  });
}
