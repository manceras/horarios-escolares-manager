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
  classGroups: {
    all: ["class-groups"] as const,
  },
  timeSlots: {
    all: ["time-slots"] as const,
  },
  schedules: {
    all: ["schedules"] as const,
    detail: (id: number) => ["schedules", id] as const,
    conflicts: (id: number) => ["schedules", id, "conflicts"] as const,
  },
} as const;
