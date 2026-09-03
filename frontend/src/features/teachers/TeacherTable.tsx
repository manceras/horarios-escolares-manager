import { useTranslation } from "react-i18next";

import type { Teacher } from "./api";

interface TeacherTableProps {
  teachers: readonly Teacher[];
}

export function TeacherTable({ teachers }: TeacherTableProps) {
  const { t } = useTranslation();

  if (teachers.length === 0) {
    return <p className="text-sm text-muted-foreground">{t("teachers.empty")}</p>;
  }

  return (
    <table className="w-full border-collapse text-sm">
      <thead>
        <tr className="border-b border-border text-left text-muted-foreground">
          <th className="py-2 font-medium">{t("teachers.name")}</th>
          <th className="py-2 font-medium">{t("teachers.email")}</th>
          <th className="py-2 font-medium">{t("teachers.specialist")}</th>
          <th className="py-2 font-medium">{t("teachers.maxPeriods")}</th>
        </tr>
      </thead>
      <tbody>
        {teachers.map((teacher) => (
          <tr key={teacher.id} className="border-b border-border/60">
            <td className="py-2">{`${teacher.first_name} ${teacher.last_name}`}</td>
            <td className="py-2">{teacher.email}</td>
            <td className="py-2">{teacher.is_specialist ? t("teachers.yes") : t("teachers.no")}</td>
            <td className="py-2">{teacher.max_periods_per_week}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
