import type { EntityFormValidator } from "@/lib/forms/useEntityForm";

import type { RoomType } from "./api";

/** Plain values a room form edits -- shared shape for both create and edit. */
export interface RoomFormValues {
  name: string;
  room_type: RoomType;
  capacity: number;
}

export const emptyRoomFormValues: RoomFormValues = {
  name: "",
  room_type: "classroom",
  capacity: 25,
};

export const validateRoomForm: EntityFormValidator<RoomFormValues> = (values) => {
  const errors: Partial<Record<keyof RoomFormValues, string>> = {};
  if (values.name.trim() === "") {
    errors.name = "rooms.validation.nameRequired";
  }
  if (!Number.isInteger(values.capacity) || values.capacity <= 0) {
    errors.capacity = "rooms.validation.capacityInvalid";
  }
  return errors;
};
