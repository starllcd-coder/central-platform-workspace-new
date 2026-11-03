"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/features/auth/store/auth.store";
import type { AuthRole, AuthUser } from "@/features/auth/types/auth.types";

type SessionResponse = {
  success: boolean;
  data?: { user: AuthUser };
};

export function useAuthSession(allowedRoles: readonly AuthRole[]) {
  const setAuthenticatedUser = useAuthStore((state) => state.setAuthenticatedUser);
  const logout = useAuthStore((state) => state.logout);

  useEffect(() => {
    let active = true;
    fetch("/api/auth/session", { cache: "no-store" })
      .then(async (response) => {
        const payload = (await response.json()) as SessionResponse;
        if (!response.ok || !payload.success || !payload.data || !allowedRoles.includes(payload.data.user.role)) {
          throw new Error("Invalid session");
        }
        if (active) setAuthenticatedUser(payload.data.user);
      })
      .catch(() => {
        if (!active) return;
        logout();
        window.location.href = allowedRoles.includes("customer") ? "/login" : "/partner-login";
      });

    return () => {
      active = false;
    };
  }, [allowedRoles, logout, setAuthenticatedUser]);
}
