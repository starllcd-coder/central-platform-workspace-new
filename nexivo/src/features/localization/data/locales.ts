import type { LocaleInfo } from "@/features/localization/types/localization.types";

export const supportedLocales: LocaleInfo[] = [
  {
    code: "en",
    englishName: "English",
    nativeName: "English",
    direction: "ltr",
    region: "International",
    enabledAtLaunch: true
  },
  {
    code: "ar",
    englishName: "Arabic",
    nativeName: "العربية",
    direction: "rtl",
    region: "GCC",
    enabledAtLaunch: true
  },
  {
    code: "de",
    englishName: "German",
    nativeName: "Deutsch",
    direction: "ltr",
    region: "Europe",
    enabledAtLaunch: false
  },
  {
    code: "fr",
    englishName: "French",
    nativeName: "Français",
    direction: "ltr",
    region: "Europe",
    enabledAtLaunch: false
  },
  {
    code: "es",
    englishName: "Spanish",
    nativeName: "Español",
    direction: "ltr",
    region: "Europe",
    enabledAtLaunch: false
  },
  {
    code: "it",
    englishName: "Italian",
    nativeName: "Italiano",
    direction: "ltr",
    region: "Europe",
    enabledAtLaunch: false
  },
  {
    code: "pt",
    englishName: "Portuguese",
    nativeName: "Português",
    direction: "ltr",
    region: "Europe",
    enabledAtLaunch: false
  },
  {
    code: "nl",
    englishName: "Dutch",
    nativeName: "Nederlands",
    direction: "ltr",
    region: "Europe",
    enabledAtLaunch: false
  },
  {
    code: "tr",
    englishName: "Turkish",
    nativeName: "Türkçe",
    direction: "ltr",
    region: "Europe",
    enabledAtLaunch: false
  },
  {
    code: "ru",
    englishName: "Russian",
    nativeName: "Русский",
    direction: "ltr",
    region: "Europe",
    enabledAtLaunch: false
  }
];

export const defaultLocale = "en";
export const rtlLocales = ["ar"];
