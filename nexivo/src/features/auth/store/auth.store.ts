"use client";

import { create } from "zustand";
import type { AuthUser } from "@/features/auth/types/auth.types";

type AuthStore = {
  user: AuthUser | null;
  isAuthenticated: boolean;
  setAuthenticatedUser: (user: AuthUser) => void;
  logout: () => void;
  updatePreferences: (preferences: Partial<Pick<AuthUser, "preferredLanguage" | "preferredCurrency" | "timezone">>) => void;
};

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: false,

  setAuthenticatedUser: (user) =>
    set({
      user,
      isAuthenticated: true
    }),

  logout: () =>
    set({
      user: null,
      isAuthenticated: false
    }),

  updatePreferences: (preferences) =>
    set((state) => ({
      user: state.user
        ? {
            ...state.user,
            ...preferences
          }
        : state.user
    }))
}));
