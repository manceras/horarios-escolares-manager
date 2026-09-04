import { useTranslation } from "react-i18next";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { UseEntityFormResult } from "@/lib/forms/useEntityForm";

import type { RoomType } from "./api";
import type { RoomFormValues } from "./room-form-values";

const ROOM_TYPES: readonly RoomType[] = ["classroom", "gym", "music", "computer_lab", "other"];

interface RoomFormProps {
  form: UseEntityFormResult<RoomFormValues>;
}

/** Fields for the create/edit dialog. Rendered inside `<EntityDialog>`. */
export function RoomForm({ form }: RoomFormProps) {
  const { t } = useTranslation();
  const { values, errors, setField } = form;

  return (
    <>
      <div className="space-y-1.5">
        <Label htmlFor="room-name">{t("rooms.name")}</Label>
        <Input
          id="room-name"
          value={values.name}
          onChange={(event) => {
            setField("name", event.target.value);
          }}
        />
        {errors.name ? <p className="text-sm text-destructive">{t(errors.name)}</p> : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="room-type">{t("rooms.type")}</Label>
        <Select
          value={values.room_type}
          onValueChange={(value) => {
            setField("room_type", value as RoomType);
          }}
        >
          <SelectTrigger id="room-type" className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ROOM_TYPES.map((roomType) => (
              <SelectItem key={roomType} value={roomType}>
                {t(`rooms.types.${roomType}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.room_type ? (
          <p className="text-sm text-destructive">{t(errors.room_type)}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="room-capacity">{t("rooms.capacity")}</Label>
        <Input
          id="room-capacity"
          type="number"
          min={1}
          value={values.capacity}
          onChange={(event) => {
            setField("capacity", Number(event.target.value));
          }}
        />
        {errors.capacity ? <p className="text-sm text-destructive">{t(errors.capacity)}</p> : null}
      </div>
    </>
  );
}
