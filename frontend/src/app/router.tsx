import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppLayout } from "@/app/AppLayout";
import { RequireAuth } from "@/app/RequireAuth";
import { LoginPage } from "@/routes/LoginPage";
import { SchedulePrintPage } from "@/routes/SchedulePrintPage";
import { TeachersPage } from "@/routes/TeachersPage";

/** One entry per URL. Pages live in `src/routes`, never inline here. */
export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    path: "/",
    element: (
      <RequireAuth>
        <AppLayout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Navigate to="/teachers" replace /> },
      { path: "teachers", element: <TeachersPage /> },
      { path: "schedules/print", element: <SchedulePrintPage /> },
    ],
  },
]);
