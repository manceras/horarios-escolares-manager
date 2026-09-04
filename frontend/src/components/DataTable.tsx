import { Pencil, Trash2 } from "lucide-react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export interface DataTableColumn<T> {
  /** Unique among the table's columns; used as the React key. */
  key: string;
  header: string;
  cell: (row: T) => ReactNode;
  className?: string;
}

export interface DataTableProps<T> {
  columns: readonly DataTableColumn<T>[];
  rows: readonly T[];
  getRowId: (row: T) => number | string;
  /** Shown instead of the table when `rows` is empty. */
  emptyMessage: string;
  onEdit?: (row: T) => void;
  onDelete?: (row: T) => void;
}

/**
 * Generic, typed listing table shared by every CRUD page. A feature wraps it
 * in a `<Entity>Table.tsx` that supplies the columns and forwards the row
 * callbacks -- see `frontend/CLAUDE.md` for the full recipe.
 */
export function DataTable<T>({
  columns,
  rows,
  getRowId,
  emptyMessage,
  onEdit,
  onDelete,
}: DataTableProps<T>) {
  const { t } = useTranslation();

  if (rows.length === 0) {
    return <p className="text-sm text-muted-foreground">{emptyMessage}</p>;
  }

  const hasActions = onEdit !== undefined || onDelete !== undefined;

  return (
    <div className="rounded-md border border-border">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead key={column.key} className={column.className}>
                {column.header}
              </TableHead>
            ))}
            {hasActions ? <TableHead className="text-right">{t("actions.title")}</TableHead> : null}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => {
            const rowId = getRowId(row);
            return (
              <TableRow key={rowId}>
                {columns.map((column) => (
                  <TableCell key={column.key} className={column.className}>
                    {column.cell(row)}
                  </TableCell>
                ))}
                {hasActions ? (
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      {onEdit ? (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          aria-label={t("actions.edit")}
                          onClick={() => {
                            onEdit(row);
                          }}
                        >
                          <Pencil className="size-4" />
                        </Button>
                      ) : null}
                      {onDelete ? (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          aria-label={t("actions.delete")}
                          onClick={() => {
                            onDelete(row);
                          }}
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      ) : null}
                    </div>
                  </TableCell>
                ) : null}
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
