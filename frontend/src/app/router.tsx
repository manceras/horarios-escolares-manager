import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppLayout } from "@/app/AppLayout";
import { RequireAuth } from "@/app/RequireAuth";
import { ClassGroupsPage } from "@/routes/ClassGroupsPage";
import { LoginPage } from "@/routes/LoginPage";
import { TeacherAvailabilityPage } from "@/routes/TeacherAvailabilityPage";
import { TeachersPage } from "@/routes/TeachersPage";
import { TimeSlotsPage } from "@/routes/TimeSlotsPage";

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
      { path: "class-groups", element: <ClassGroupsPage /> },
      { path: "time-slots", element: <TimeSlotsPage /> },
      { path: "teacher-availability", element: <TeacherAvailabilityPage /> },
    ],
  },
]);
