import { useTranslation } from "react-i18next";

import { QueryState } from "@/components/QueryState";
import { TeacherTable } from "@/features/teachers/TeacherTable";
import { useTeachers } from "@/features/teachers/api";

/**
 * Reference route: composition only. Data comes from a feature hook, states are
 * delegated, and there is no business logic here.
 */
export function TeachersPage() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useTeachers();

  return (
    <section className="space-y-4">
      <h1 className="text-xl font-semibold">{t("teachers.title")}</h1>
      <QueryState
        isLoading={isLoading}
        error={error}
        onRetry={() => {
          void refetch();
        }}
      />
      {data ? <TeacherTable teachers={data} /> : null}
    </section>
  );
}
