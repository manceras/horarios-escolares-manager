import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { getErrorMessageKeys } from "@/lib/api/error-translation";

interface QueryStateProps {
  isLoading: boolean;
  error: unknown;
  onRetry?: () => void;
}

/**
 * Loading and error presentation shared by every page. Error codes are
 * translated; a raw backend message is never shown to the user.
 */
export function QueryState({ isLoading, error, onRetry }: QueryStateProps) {
  const { t } = useTranslation();

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">{t("app.loading")}</p>;
  }

  if (error !== null && error !== undefined) {
    return (
      <div className="flex items-center gap-3">
        <p className="text-sm text-destructive">{t(getErrorMessageKeys(error))}</p>
        {onRetry ? (
          <Button variant="outline" size="sm" onClick={onRetry}>
            {t("app.retry")}
          </Button>
        ) : null}
      </div>
    );
  }

  return null;
}
