import { en } from "@/features/localization/data/messages.en";
import { ar } from "@/features/localization/data/messages.ar";
import type { SupportedLocale } from "@/features/localization/types/localization.types";

const europeanFallback = en;

export const messages = {
  en,
  ar,
  de: europeanFallback,
  fr: europeanFallback,
  es: europeanFallback,
  it: europeanFallback,
  pt: europeanFallback,
  nl: europeanFallback,
  tr: europeanFallback,
  ru: europeanFallback
};

export function getMessages(locale: SupportedLocale) {
  return messages[locale] ?? messages.en;
}
