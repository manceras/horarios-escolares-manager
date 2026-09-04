import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getErrorMessageKeys } from "@/lib/api/error-translation";

export interface ConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string | undefined;
  onConfirm: () => void;
  isConfirming: boolean;
  /**
   * A mutation's `error`, if the last confirm failed -- e.g. a 409 when
   * deleting a room that is still referenced by a curriculum entry. Shown
   * translated inside the dialog instead of failing silently; the dialog
   * stays open so the user sees why.
   */
  error?: unknown;
  confirmLabel?: string | undefined;
}

/** Confirmation modal for destructive actions, shared by every CRUD page. */
export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  onConfirm,
  isConfirming,
  error,
  confirmLabel,
}: ConfirmDialogProps) {
  const { t } = useTranslation();
  const hasError = error !== null && error !== undefined;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description ? <DialogDescription>{description}</DialogDescription> : null}
        </DialogHeader>
        {hasError ? (
          <p className="text-sm text-destructive">{t(getErrorMessageKeys(error))}</p>
        ) : null}
        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            disabled={isConfirming}
            onClick={() => {
              onOpenChange(false);
            }}
          >
            {t("app.cancel")}
          </Button>
          <Button type="button" variant="destructive" disabled={isConfirming} onClick={onConfirm}>
            {isConfirming ? t("app.saving") : (confirmLabel ?? t("actions.delete"))}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
