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
  classGroups: {
    all: ["class-groups"] as const,
    detail: (id: number) => ["class-groups", id] as const,
  },
  timeSlots: {
    all: ["time-slots"] as const,
    detail: (id: number) => ["time-slots", id] as const,
  },
  teacherUnavailabilities: {
    byTeacher: (teacherId: number) => ["teacher-unavailabilities", teacherId] as const,
  },
  curriculumEntries: {
    all: ["curriculum-entries"] as const,
    workload: ["curriculum-entries", "workload"] as const,
  },
  schedules: {
    all: ["schedules"] as const,
    detail: (id: number) => ["schedules", id] as const,
    conflicts: (id: number) => ["schedules", id, "conflicts"] as const,
  },
} as const;
