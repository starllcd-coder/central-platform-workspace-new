import type { SupportedLocale, TextDirection } from "@/features/localization/types/localization.types";
import { supportedLocales } from "@/features/localization/data/locales";

export function getLocaleInfo(locale: SupportedLocale) {
  return supportedLocales.find((item) => item.code === locale) ?? supportedLocales[0];
}

export function getTextDirection(locale: SupportedLocale): TextDirection {
  return getLocaleInfo(locale).direction;
}

export function isRtlLocale(locale: SupportedLocale): boolean {
  return getTextDirection(locale) === "rtl";
}

export function getBrowserLocale(): SupportedLocale {
  if (typeof window === "undefined") return "en";

  const browserLanguage = window.navigator.language.split("-")[0];

  const match = supportedLocales.find((item) => item.code === browserLanguage);

  return match?.code ?? "en";
}
