import { MutationCache, QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { getErrorMessageKeys } from "@/lib/api/error-translation";
import i18n from "@/lib/i18n";

declare module "@tanstack/react-query" {
  interface Register {
    mutationMeta: {
      /**
       * i18n key for the toast shown when the mutation succeeds. Omit it for
       * a mutation that should stay silent on success (a background write).
       */
      successMessageKey?: string;
    };
  }
}

/**
 * Toast feedback for every mutation in the app, wired once here instead of
 * once per feature. Success needs a per-entity message, so a mutation opts
 * in with `meta: { successMessageKey: "teachers.createSuccess" }`; failure
 * is always shown, translated through the same helper `QueryState` uses so
 * the two never drift apart.
 */
const mutationCache = new MutationCache({
  onSuccess: (_data, _variables, _context, mutation) => {
    const key = mutation.meta?.successMessageKey;
    if (key !== undefined) {
      toast.success(i18n.t(key));
    }
  },
  onError: (error) => {
    toast.error(i18n.t(getErrorMessageKeys(error)));
  },
});

export const queryClient = new QueryClient({
  mutationCache,
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
