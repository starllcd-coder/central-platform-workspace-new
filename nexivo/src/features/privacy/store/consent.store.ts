"use client";

import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type {
  ConsentCategory,
  ConsentPreference
} from "@/features/privacy/types/privacy.types";
import { defaultConsentPreferences } from "@/features/privacy/data/privacy-data";

type ConsentStore = {
  preferences: ConsentPreference[];
  hasHydrated: boolean;
  hasSavedConsent: boolean;
  toggleConsent: (category: ConsentCategory) => void;
  acceptAll: () => void;
  rejectOptional: () => void;
  saveConsent: () => void;
  resetConsent: () => void;
  setHasHydrated: (hasHydrated: boolean) => void;
};

export const useConsentStore = create<ConsentStore>()(
  persist(
    (set) => ({
      preferences: defaultConsentPreferences,
      hasHydrated: false,
      hasSavedConsent: false,

      toggleConsent: (category) =>
        set((state) => ({
          preferences: state.preferences.map((preference) =>
            preference.category === category && !preference.required
              ? { ...preference, enabled: !preference.enabled }
              : preference
          )
        })),

      acceptAll: () =>
        set((state) => ({
          preferences: state.preferences.map((preference) => ({
            ...preference,
            enabled: true
          })),
          hasSavedConsent: true
        })),

      rejectOptional: () =>
        set((state) => ({
          preferences: state.preferences.map((preference) => ({
            ...preference,
            enabled: preference.required
          })),
          hasSavedConsent: true
        })),

      saveConsent: () => set({ hasSavedConsent: true }),

      resetConsent: () =>
        set({
          preferences: defaultConsentPreferences,
          hasSavedConsent: false
        }),

      setHasHydrated: (hasHydrated) => set({ hasHydrated })
    }),
    {
      name: "nexivo-consent-preferences",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        preferences: state.preferences,
        hasSavedConsent: state.hasSavedConsent
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      }
    }
  )
);
