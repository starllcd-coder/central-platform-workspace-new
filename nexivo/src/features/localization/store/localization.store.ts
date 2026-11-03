"use client";

import { create } from "zustand";
import type { SupportedLocale, TextDirection } from "@/features/localization/types/localization.types";
import { getTextDirection } from "@/features/localization/utils/locale-utils";

type LocalizationStore = {
  locale: SupportedLocale;
  direction: TextDirection;
  setLocale: (locale: SupportedLocale) => void;
};

export const useLocalizationStore = create<LocalizationStore>((set) => ({
  locale: "en",
  direction: "ltr",

  setLocale: (locale) =>
    set({
      locale,
      direction: getTextDirection(locale)
    })
}));
