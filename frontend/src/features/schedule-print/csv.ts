import {
  formatTime,
  type WeekGridCell,
  type WeekGridRow,
} from "@/features/schedule-print/print-model";

/** Spanish Excel expects `;` as the field separator, not `,`. */
const FIELD_SEPARATOR = ";";
const LINE_BREAK = "\r\n";
/** Without a BOM, Excel on Windows/Spanish locale mis-detects the encoding and mangles accents. */
const UTF8_BOM = "﻿";

export interface CsvSheet {
  title: string;
  rows: WeekGridRow[];
}

function cellToText(cell: WeekGridCell | undefined): string {
  if (cell === undefined) return "";
  return cell.lines.filter((line) => line !== "").join(" - ");
}

function escapeField(value: string): string {
  if (value.includes(FIELD_SEPARATOR) || value.includes('"') || /[\r\n]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function toCsvLine(fields: string[]): string {
  return fields.map(escapeField).join(FIELD_SEPARATOR);
}

/**
 * Renders one or more printed weeks as a single `;`-separated CSV, one
 * section per sheet (used both for a single entity and for "all").
 */
export function buildCsv(
  sheets: CsvSheet[],
  weekdayLabels: readonly string[],
  timeLabel: string,
  breakLabel: string,
): string {
  const lines: string[] = [];

  for (const sheet of sheets) {
    lines.push(toCsvLine([sheet.title]));
    lines.push(toCsvLine([timeLabel, ...weekdayLabels]));

    for (const row of sheet.rows) {
      const timeRange = `${formatTime(row.startTime)}-${formatTime(row.endTime)}`;
      const cells = row.isBreak
        ? weekdayLabels.map(() => breakLabel)
        : row.cellsByDay.map(cellToText);
      lines.push(toCsvLine([timeRange, ...cells]));
    }

    lines.push("");
  }

  return lines.join(LINE_BREAK);
}

/** Triggers a client-side download of `content` as a UTF-8 CSV file. */
export function downloadCsv(filename: string, content: string): void {
  const blob = new Blob([UTF8_BOM + content], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
