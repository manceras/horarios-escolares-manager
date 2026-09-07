import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { UpdateBanner } from "@/features/updates/UpdateBanner";
import { cn } from "@/lib/utils";

// Ordered the way a school sets its timetable up: staff, then structure, then
// what each group studies.
const NAV_ITEMS = [
  { to: "/teachers", labelKey: "nav.teachers" },
  { to: "/teacher-availability", labelKey: "nav.availability" },
  { to: "/class-groups", labelKey: "nav.groups" },
  { to: "/subjects", labelKey: "nav.subjects" },
  { to: "/rooms", labelKey: "nav.rooms" },
  { to: "/time-slots", labelKey: "nav.timeSlots" },
  { to: "/curriculum", labelKey: "nav.curriculum" },
  { to: "/schedules/print", labelKey: "nav.print" },
  { to: "/schedules", labelKey: "nav.schedules" },
] as const;

export function AppLayout() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen">
      <header className="border-b border-border print:hidden">
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
        </div>
      </header>
      <UpdateBanner />
      <main className="mx-auto max-w-5xl px-4 py-6 print:max-w-none print:p-0">
        <Outlet />
      </main>
    </div>
  );
}
