/**
 * `TimeSlot.day_of_week` is 0 (Monday) through 4 (Friday). This is the single
 * place that maps that index to its `app.weekdays.*` i18n key, so a raw
 * number never has to be formatted ad hoc in a component.
 */
export const WEEKDAY_KEYS = ["monday", "tuesday", "wednesday", "thursday", "friday"] as const;

export type WeekdayIndex = 0 | 1 | 2 | 3 | 4;

export const WEEKDAY_INDICES: readonly WeekdayIndex[] = [0, 1, 2, 3, 4];

export function weekdayTranslationKey(dayOfWeek: number): string {
  const key = WEEKDAY_KEYS[dayOfWeek];
  return key !== undefined ? `app.weekdays.${key}` : "app.weekdays.unknown";
}

/** Lookup key for a (day, period) cell in a weekly grid. */
export function dayPeriodKey(dayOfWeek: number, periodIndex: number): string {
  return [dayOfWeek, periodIndex].join("-");
}
