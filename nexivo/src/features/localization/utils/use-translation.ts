"use client";

import type { SupportedLocale } from "@/features/localization/types/localization.types";
import { getMessages } from "@/features/localization/data/messages";
import { useLocalizationStore } from "@/features/localization/store/localization.store";

type TranslationPath =
  | "common.appName"
  | "common.companyName"
  | "common.bookNow"
  | "common.requestDemo"
  | "common.listYourBusiness"
  | "common.login"
  | "common.register"
  | "common.search"
  | "common.language"
  | "common.currency"
  | "common.continue"
  | "common.save"
  | "common.cancel"
  | "nav.stays"
  | "nav.cars"
  | "nav.laundry"
  | "nav.destinations"
  | "nav.business"
  | "nav.pricing"
  | "nav.about"
  | "nav.contact"
  | "home.eyebrow"
  | "home.title"
  | "home.description";

function readPath(source: Record<string, unknown>, path: string): string {
  const value = path.split(".").reduce<unknown>((current, key) => {
    if (current && typeof current === "object" && key in current) {
      return (current as Record<string, unknown>)[key];
    }

    return undefined;
  }, source);

  return typeof value === "string" ? value : path;
}

export function useTranslation() {
  const { locale } = useLocalizationStore();
  const dictionary = getMessages(locale as SupportedLocale);

  function t(path: TranslationPath): string {
    return readPath(dictionary, path);
  }

  return {
    t,
    locale
  };
}
