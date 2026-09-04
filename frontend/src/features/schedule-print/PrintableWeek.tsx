import { useTranslation } from "react-i18next";

import { formatTime, WEEKDAYS, type WeekGridRow } from "@/features/schedule-print/print-model";

interface PrintableWeekProps {
  heading: string;
  rows: WeekGridRow[];
  /** Renders a page break after this sheet when printing (all but the last of a batch). */
  breakAfter: boolean;
}

/**
 * One week rendered as a table: time slots down the side, weekdays across.
 * Used both on screen and, via `schedule-print.css`, on paper -- one sheet
 * per printed page.
 */
export function PrintableWeek({ heading, rows, breakAfter }: PrintableWeekProps) {
  const { t } = useTranslation();

  return (
    <section
      className={`schedule-print-sheet rounded-lg border border-border p-4 print:rounded-none print:border-0 print:p-0 ${
        breakAfter ? "schedule-print-break-after" : ""
      }`}
    >
      <h2 className="mb-3 text-lg font-semibold">{heading}</h2>
      <table className="schedule-print-table w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="border border-border bg-muted px-2 py-1 text-left font-medium">
              {t("print.columns.time")}
            </th>
            {WEEKDAYS.map(({ key }) => (
              <th
                key={key}
                className="border border-border bg-muted px-2 py-1 text-left font-medium"
              >
                {t(`app.weekdays.${key}`)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row.periodIndex}
              className={row.isBreak ? "schedule-print-break-row bg-muted/60" : undefined}
            >
              <td className="border border-border px-2 py-1 align-top whitespace-nowrap">
                {formatTime(row.startTime)}–{formatTime(row.endTime)}
              </td>
              {row.isBreak ? (
                <td
                  colSpan={WEEKDAYS.length}
                  className="border border-border px-2 py-1 text-center italic text-muted-foreground"
                >
                  {t("print.break")}
                </td>
              ) : (
                row.cellsByDay.map((cell, index) => (
                  <td key={index} className="border border-border px-2 py-1 align-top">
                    {cell
                      ? cell.lines
                          .filter((line) => line !== "")
                          .map((line, lineIndex) => (
                            <div
                              key={lineIndex}
                              className={lineIndex === 0 ? "font-medium" : "text-muted-foreground"}
                            >
                              {line}
                            </div>
                          ))
                      : null}
                  </td>
                ))
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
