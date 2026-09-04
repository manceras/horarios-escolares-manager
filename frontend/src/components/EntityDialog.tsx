import type { ReactNode, SubmitEvent } from "react";
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

export interface EntityDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string | undefined;
  /** The dialog only renders the shell; the caller supplies the form fields. */
  children: ReactNode;
  onSubmit: (event: SubmitEvent<HTMLFormElement>) => void;
  isSubmitting: boolean;
  /** A mutation's `error`, if the last submit failed. Translated the same way as `QueryState`. */
  error?: unknown;
  submitLabel?: string | undefined;
}

/**
 * Create/edit modal shared by every CRUD page. It owns the submit button's
 * disabled/loading state and the translated error banner; it does not own
 * the open state or the mutation -- the caller flips `open` to `false` from
 * the mutation's `onSuccess`, which is what "closes on success" means here.
 */
export function EntityDialog({
  open,
  onOpenChange,
  title,
  description,
  children,
  onSubmit,
  isSubmitting,
  error,
  submitLabel,
}: EntityDialogProps) {
  const { t } = useTranslation();
  const hasError = error !== null && error !== undefined;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description ? <DialogDescription>{description}</DialogDescription> : null}
        </DialogHeader>
        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-4">{children}</div>
          {hasError ? (
            <p className="text-sm text-destructive">{t(getErrorMessageKeys(error))}</p>
          ) : null}
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              disabled={isSubmitting}
              onClick={() => {
                onOpenChange(false);
              }}
            >
              {t("app.cancel")}
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? t("app.saving") : (submitLabel ?? t("app.save"))}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
