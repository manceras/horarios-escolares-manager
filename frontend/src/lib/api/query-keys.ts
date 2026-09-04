/**
 * Every TanStack Query key lives here. Never inline a key array in a component:
 * invalidation depends on these being written in exactly one place.
 */
export const queryKeys = {
  currentUser: ["current-user"] as const,
  teachers: {
    all: ["teachers"] as const,
    detail: (id: number) => ["teachers", id] as const,
  },
  rooms: {
    all: ["rooms"] as const,
    detail: (id: number) => ["rooms", id] as const,
  },
  subjects: {
    all: ["subjects"] as const,
    detail: (id: number) => ["subjects", id] as const,
  },
} as const;
