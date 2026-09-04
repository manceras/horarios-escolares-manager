import { useTranslation } from "react-i18next";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Schedule } from "@/features/schedule-print/api";
import { VIEW_TYPES, type ViewEntity, type ViewType } from "@/features/schedule-print/print-model";

const ALL_VALUE = "all";

interface ViewSelectorProps {
  schedules: Schedule[];
  scheduleId: number | undefined;
  onScheduleChange: (id: number) => void;
  viewType: ViewType;
  onViewTypeChange: (viewType: ViewType) => void;
  entities: ViewEntity[];
  selection: number | "all";
  onSelectionChange: (selection: number | "all") => void;
}

/**
 * The three controls that choose what gets printed: which schedule, which
 * axis to slice it by (teacher / class group / room), and which one of
 * those -- or every one of them, laid out as one page per entity.
 */
export function ViewSelector({
  schedules,
  scheduleId,
  onScheduleChange,
  viewType,
  onViewTypeChange,
  entities,
  selection,
  onSelectionChange,
}: ViewSelectorProps) {
  const { t } = useTranslation();

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div className="space-y-1.5">
        <Label htmlFor="print-schedule">{t("print.scheduleLabel")}</Label>
        <Select
          {...(scheduleId !== undefined ? { value: String(scheduleId) } : {})}
          onValueChange={(value) => {
            onScheduleChange(Number(value));
          }}
        >
          <SelectTrigger id="print-schedule" className="w-full">
            <SelectValue placeholder={t("print.scheduleLabel")} />
          </SelectTrigger>
          <SelectContent>
            {schedules.map((schedule) => (
              <SelectItem key={schedule.id} value={String(schedule.id)}>
                {schedule.name} ({t(`print.scheduleStatus.${schedule.status}`)})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="print-view-type">{t("print.viewTypeLabel")}</Label>
        <Select
          value={viewType}
          onValueChange={(value) => {
            onViewTypeChange(value as ViewType);
          }}
        >
          <SelectTrigger id="print-view-type" className="w-full">
            <SelectValue placeholder={t("print.viewTypeLabel")} />
          </SelectTrigger>
          <SelectContent>
            {VIEW_TYPES.map((type) => (
              <SelectItem key={type} value={type}>
                {t(`print.viewType.${type}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="print-entity">{t("print.entityLabel")}</Label>
        <Select
          value={selection === ALL_VALUE ? ALL_VALUE : String(selection)}
          onValueChange={(value) => {
            onSelectionChange(value === ALL_VALUE ? ALL_VALUE : Number(value));
          }}
        >
          <SelectTrigger id="print-entity" className="w-full">
            <SelectValue placeholder={t("print.entityLabel")} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL_VALUE}>{t("print.all")}</SelectItem>
            {entities.map((entity) => (
              <SelectItem key={entity.id} value={String(entity.id)}>
                {entity.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
