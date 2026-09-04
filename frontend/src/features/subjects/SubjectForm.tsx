import { useTranslation } from "react-i18next";

import type { RoomType } from "@/features/rooms/api";
import type { UseEntityFormResult } from "@/lib/forms/useEntityForm";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import type { SubjectFormValues } from "./subject-form-values";

const ROOM_TYPES: readonly RoomType[] = ["classroom", "gym", "music", "computer_lab", "other"];

/** Sentinel select value standing in for `null` -- "no aula especial requerida". */
const NO_REQUIRED_ROOM_TYPE = "none";

interface SubjectFormProps {
  form: UseEntityFormResult<SubjectFormValues>;
}

/** Fields for the create/edit dialog. Rendered inside `<EntityDialog>`. */
export function SubjectForm({ form }: SubjectFormProps) {
  const { t } = useTranslation();
  const { values, errors, setField } = form;

  return (
    <>
      <div className="space-y-1.5">
        <Label htmlFor="subject-code">{t("subjects.code")}</Label>
        <Input
          id="subject-code"
          value={values.code}
          onChange={(event) => {
            setField("code", event.target.value);
          }}
        />
        {errors.code ? <p className="text-sm text-destructive">{t(errors.code)}</p> : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="subject-name">{t("subjects.name")}</Label>
        <Input
          id="subject-name"
          value={values.name}
          onChange={(event) => {
            setField("name", event.target.value);
          }}
        />
        {errors.name ? <p className="text-sm text-destructive">{t(errors.name)}</p> : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="subject-required-room-type">{t("subjects.requiredRoomType")}</Label>
        <Select
          value={values.required_room_type ?? NO_REQUIRED_ROOM_TYPE}
          onValueChange={(value) => {
            setField(
              "required_room_type",
              value === NO_REQUIRED_ROOM_TYPE ? null : (value as RoomType),
            );
          }}
        >
          <SelectTrigger id="subject-required-room-type" className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={NO_REQUIRED_ROOM_TYPE}>
              {t("subjects.noRequiredRoomType")}
            </SelectItem>
            {ROOM_TYPES.map((roomType) => (
              <SelectItem key={roomType} value={roomType}>
                {t(`rooms.types.${roomType}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.required_room_type ? (
          <p className="text-sm text-destructive">{t(errors.required_room_type)}</p>
        ) : null}
      </div>
    </>
  );
}
