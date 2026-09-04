import { useTranslation } from "react-i18next";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import type { CurriculumEntry } from "./api";

interface CurriculumTableProps {
  entries: readonly CurriculumEntry[];
  onEdit: (entry: CurriculumEntry) => void;
  onDelete: (entry: CurriculumEntry) => void;
}

interface CurriculumGroup {
  classGroupId: number;
  classGroupName: string;
  entries: CurriculumEntry[];
  totalPeriods: number;
}

/**
 * A flat list is unreadable once a school has a few dozen entries: a head of
 * studies thinks in terms of "what does this group study", not in rows. Group
 * by class group and carry a running subtotal of periods per group.
 */
function groupByClassGroup(entries: readonly CurriculumEntry[]): CurriculumGroup[] {
  const groups = new Map<number, CurriculumGroup>();
  for (const entry of entries) {
    const existing = groups.get(entry.class_group_id);
    if (existing) {
      existing.entries.push(entry);
      existing.totalPeriods += entry.periods_per_week;
    } else {
      groups.set(entry.class_group_id, {
        classGroupId: entry.class_group_id,
        classGroupName: entry.class_group_name,
        entries: [entry],
        totalPeriods: entry.periods_per_week,
      });
    }
  }
  return [...groups.values()].sort((a, b) => a.classGroupName.localeCompare(b.classGroupName));
}

export function CurriculumTable({ entries, onEdit, onDelete }: CurriculumTableProps) {
  const { t } = useTranslation();

  const columns: DataTableColumn<CurriculumEntry>[] = [
    { key: "subject", header: t("curriculum.subject"), cell: (entry) => entry.subject_name },
    { key: "teacher", header: t("curriculum.teacher"), cell: (entry) => entry.teacher_name },
    {
      key: "periods",
      header: t("curriculum.periodsPerWeek"),
      cell: (entry) => entry.periods_per_week,
    },
  ];

  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">{t("curriculum.empty")}</p>;
  }

  const groups = groupByClassGroup(entries);

  return (
    <div className="space-y-4">
      {groups.map((group) => (
        <Card key={group.classGroupId}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>{group.classGroupName}</CardTitle>
            <span className="text-sm text-muted-foreground">
              {t("curriculum.groupSubtotal", { count: group.totalPeriods })}
            </span>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={columns}
              rows={group.entries}
              getRowId={(entry) => entry.id}
              emptyMessage={t("curriculum.empty")}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
