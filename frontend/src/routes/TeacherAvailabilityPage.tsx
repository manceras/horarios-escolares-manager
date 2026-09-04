import { useState } from "react";
import { useTranslation } from "react-i18next";

import { QueryState } from "@/components/QueryState";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  useTeacherUnavailabilities,
  useReplaceTeacherUnavailabilities,
} from "@/features/teacher-availability/api";
import { TeacherAvailabilityGrid } from "@/features/teacher-availability/TeacherAvailabilityGrid";
import { useTeachers } from "@/features/teachers/api";
import { useTimeSlots } from "@/features/time-slots/api";

/**
 * Pick a teacher, then edit their whole weekly availability at once. The
 * most valuable of the three screens: it drives the "teacher availability"
 * hard constraint the solver enforces.
 */
export function TeacherAvailabilityPage() {
  const { t } = useTranslation();
  const {
    data: teachers,
    isLoading: teachersLoading,
    error: teachersError,
    refetch: refetchTeachers,
  } = useTeachers();
  const [teacherId, setTeacherId] = useState<number | null>(null);

  return (
    <section className="space-y-4">
      <h1 className="text-xl font-semibold">{t("availability.title")}</h1>

      <QueryState
        isLoading={teachersLoading}
        error={teachersError}
        onRetry={() => {
          void refetchTeachers();
        }}
      />

      {teachers ? (
        <div className="max-w-sm space-y-1.5">
          <Label htmlFor="availability-teacher">{t("availability.teacher")}</Label>
          <Select
            {...(teacherId !== null ? { value: String(teacherId) } : {})}
            onValueChange={(value) => {
              setTeacherId(Number(value));
            }}
          >
            <SelectTrigger id="availability-teacher" className="w-full">
              <SelectValue placeholder={t("availability.selectTeacherPlaceholder")} />
            </SelectTrigger>
            <SelectContent>
              {teachers.map((teacher) => (
                <SelectItem key={teacher.id} value={String(teacher.id)}>
                  {`${teacher.first_name} ${teacher.last_name}`}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      ) : null}

      {teacherId !== null ? (
        <TeacherAvailabilityLoader key={teacherId} teacherId={teacherId} />
      ) : null}
    </section>
  );
}

interface TeacherAvailabilityLoaderProps {
  teacherId: number;
}

/** Loads the slots and the teacher's current unavailability, then hands the grid a ready snapshot. */
function TeacherAvailabilityLoader({ teacherId }: TeacherAvailabilityLoaderProps) {
  const { t } = useTranslation();
  const {
    data: timeSlots,
    isLoading: slotsLoading,
    error: slotsError,
    refetch: refetchSlots,
  } = useTimeSlots();
  const {
    data: unavailabilities,
    isLoading: unavailabilitiesLoading,
    error: unavailabilitiesError,
    refetch: refetchUnavailabilities,
  } = useTeacherUnavailabilities(teacherId);
  const replaceUnavailabilities = useReplaceTeacherUnavailabilities(teacherId);

  const isLoading = slotsLoading || unavailabilitiesLoading;
  const error = slotsError ?? unavailabilitiesError;

  if (isLoading || error || !timeSlots || !unavailabilities) {
    return (
      <QueryState
        isLoading={isLoading}
        error={error}
        onRetry={() => {
          void refetchSlots();
          void refetchUnavailabilities();
        }}
      />
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("availability.gridTitle")}</CardTitle>
      </CardHeader>
      <CardContent>
        <TeacherAvailabilityGrid
          timeSlots={timeSlots}
          initialUnavailableSlotIds={unavailabilities.map((entry) => entry.time_slot_id)}
          replaceUnavailabilities={replaceUnavailabilities}
        />
      </CardContent>
    </Card>
  );
}
