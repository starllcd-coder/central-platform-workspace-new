export type SupportedLocale =
  | "en"
  | "ar"
  | "de"
  | "fr"
  | "es"
  | "it"
  | "pt"
  | "nl"
  | "tr"
  | "ru";

export type TextDirection = "ltr" | "rtl";

export type LocaleInfo = {
  code: SupportedLocale;
  englishName: string;
  nativeName: string;
  direction: TextDirection;
  region: "GCC" | "Europe" | "International";
  enabledAtLaunch: boolean;
};
