/**
 * The API returns `TimeSlot` times as `"09:00:00"` (HH:MM:SS). The UI always
 * shows and edits them as `"09:00"` (HH:MM) -- this is the one place that
 * does the conversion in either direction.
 */
export function formatTime(time: string): string {
  return time.slice(0, 5);
}
