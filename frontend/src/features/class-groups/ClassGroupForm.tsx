import { useTranslation } from "react-i18next";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useTeachers } from "@/features/teachers/api";
import type { UseEntityFormResult } from "@/lib/forms/useEntityForm";

import { useRoomOptions } from "./api";
import type { ClassGroupFormValues } from "./class-group-form-values";

interface ClassGroupFormProps {
  form: UseEntityFormResult<ClassGroupFormValues>;
}

/** No teacher/room selected -- Radix `Select` reserves the empty string, so this sentinel stands in for `null`. */
const UNASSIGNED = "unassigned";

/** Fields for the create/edit dialog. Rendered inside `<EntityDialog>`. */
export function ClassGroupForm({ form }: ClassGroupFormProps) {
  const { t } = useTranslation();
  const { values, errors, setField } = form;
  const { data: teachers } = useTeachers();
  const { data: rooms } = useRoomOptions();

  return (
    <>
      <div className="space-y-1.5">
        <Label htmlFor="class-group-name">{t("classGroups.name")}</Label>
        <Input
          id="class-group-name"
          value={values.name}
          onChange={(event) => {
            setField("name", event.target.value);
          }}
        />
        {errors.name ? <p className="text-sm text-destructive">{t(errors.name)}</p> : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="class-group-grade">{t("classGroups.grade")}</Label>
        <Input
          id="class-group-grade"
          type="number"
          min={1}
          max={6}
          value={values.grade}
          onChange={(event) => {
            setField("grade", Number(event.target.value));
          }}
        />
        {errors.grade ? <p className="text-sm text-destructive">{t(errors.grade)}</p> : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="class-group-tutor">{t("classGroups.tutor")}</Label>
        <Select
          value={values.tutor_id !== null ? String(values.tutor_id) : UNASSIGNED}
          onValueChange={(value) => {
            setField("tutor_id", value === UNASSIGNED ? null : Number(value));
          }}
        >
          <SelectTrigger id="class-group-tutor" className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={UNASSIGNED}>{t("classGroups.unassigned")}</SelectItem>
            {(teachers ?? []).map((teacher) => (
              <SelectItem key={teacher.id} value={String(teacher.id)}>
                {`${teacher.first_name} ${teacher.last_name}`}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="class-group-home-room">{t("classGroups.homeRoom")}</Label>
        <Select
          value={values.home_room_id !== null ? String(values.home_room_id) : UNASSIGNED}
          onValueChange={(value) => {
            setField("home_room_id", value === UNASSIGNED ? null : Number(value));
          }}
        >
          <SelectTrigger id="class-group-home-room" className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={UNASSIGNED}>{t("classGroups.unassigned")}</SelectItem>
            {(rooms ?? []).map((room) => (
              <SelectItem key={room.id} value={String(room.id)}>
                {room.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </>
  );
}
