import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { clearToken } from "@/lib/api/client";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/teachers", labelKey: "nav.teachers" },
  { to: "/rooms", labelKey: "nav.rooms" },
  { to: "/subjects", labelKey: "nav.subjects" },
] as const;

export function AppLayout() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <header className="border-b border-border">
        <div className="mx-auto flex max-w-5xl items-center gap-6 px-4 py-3">
          <span className="font-semibold">{t("app.title")}</span>
          <nav className="flex gap-4 text-sm">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn("hover:text-primary", isActive && "font-medium text-primary")
                }
              >
                {t(item.labelKey)}
              </NavLink>
            ))}
          </nav>
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto"
            onClick={() => {
              clearToken();
              void navigate("/login");
            }}
          >
            {t("nav.logout")}
          </Button>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
