import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { getStoredToken } from "@/lib/api/client";

/** Sends anonymous visitors to the login page. */
export function RequireAuth({ children }: { children: ReactNode }) {
  if (getStoredToken() === null) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
