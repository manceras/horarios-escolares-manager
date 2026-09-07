import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppLayout } from "@/app/AppLayout";
import { ClassGroupsPage } from "@/routes/ClassGroupsPage";
import { CurriculumPage } from "@/routes/CurriculumPage";
import { RoomsPage } from "@/routes/RoomsPage";
import { SubjectsPage } from "@/routes/SubjectsPage";
import { TeacherAvailabilityPage } from "@/routes/TeacherAvailabilityPage";
import { SchedulePrintPage } from "@/routes/SchedulePrintPage";
import { SchedulePage } from "@/routes/SchedulePage";
import { SchedulesPage } from "@/routes/SchedulesPage";
import { TeachersPage } from "@/routes/TeachersPage";
import { TimeSlotsPage } from "@/routes/TimeSlotsPage";

/** One entry per URL. Pages live in `src/routes`, never inline here. */
export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/teachers" replace /> },
      { path: "teachers", element: <TeachersPage /> },
      { path: "teacher-availability", element: <TeacherAvailabilityPage /> },
      { path: "class-groups", element: <ClassGroupsPage /> },
      { path: "subjects", element: <SubjectsPage /> },
      { path: "rooms", element: <RoomsPage /> },
      { path: "time-slots", element: <TimeSlotsPage /> },
      { path: "curriculum", element: <CurriculumPage /> },
      { path: "schedules/print", element: <SchedulePrintPage /> },
      { path: "schedules", element: <SchedulesPage /> },
      { path: "schedules/:scheduleId", element: <SchedulePage /> },
    ],
  },
]);
