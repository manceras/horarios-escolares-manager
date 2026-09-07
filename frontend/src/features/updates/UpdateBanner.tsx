import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { useInstallUpdate, useUpdateStatus } from "@/features/updates/api";

/**
 * Tells the user a new version exists and installs it in one click.
 *
 * Deliberately a strip above the page rather than a modal: a school opening the
 * program to print tomorrow's timetable should never have to dismiss something
 * first. It stays until they take it.
 */
export function UpdateBanner() {
  const { t } = useTranslation();
  const { data } = useUpdateStatus();
  const install = useInstallUpdate();

  if (!data?.update_available) return null;

  return (
    <div className="border-b border-border bg-muted print:hidden">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-3 px-4 py-2 text-sm">
        <span>{t("updates.available", { version: data.latest_version ?? "" })}</span>
        {data.can_install ? (
          <Button
            size="sm"
            variant="primary"
            disabled={install.isPending}
            onClick={() => {
              install.mutate();
            }}
          >
            {install.isPending ? t("updates.installing") : t("updates.install")}
          </Button>
        ) : (
          <span className="text-muted-foreground">{t("updates.manualHint")}</span>
        )}
      </div>
    </div>
  );
}
