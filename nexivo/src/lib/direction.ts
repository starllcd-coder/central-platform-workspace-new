export type Direction = "ltr" | "rtl";

export function getDirection(locale: string): Direction {
  return locale === "ar" ? "rtl" : "ltr";
}

export function isRtl(locale: string): boolean {
  return getDirection(locale) === "rtl";
}
