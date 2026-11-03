export const localeOptions = [
  { code: "en", label: "English", nativeLabel: "English", direction: "ltr" },
  { code: "ar", label: "Arabic", nativeLabel: "العربية", direction: "rtl" },
  { code: "de", label: "German", nativeLabel: "Deutsch", direction: "ltr" },
  { code: "fr", label: "French", nativeLabel: "Français", direction: "ltr" },
  { code: "es", label: "Spanish", nativeLabel: "Español", direction: "ltr" },
  { code: "it", label: "Italian", nativeLabel: "Italiano", direction: "ltr" },
  { code: "pt", label: "Portuguese", nativeLabel: "Português", direction: "ltr" },
  { code: "nl", label: "Dutch", nativeLabel: "Nederlands", direction: "ltr" },
  { code: "tr", label: "Turkish", nativeLabel: "Türkçe", direction: "ltr" },
  { code: "ru", label: "Russian", nativeLabel: "Русский", direction: "ltr" }
] as const;

export const currencyOptions = [
  { code: "OMR", label: "Omani Rial", symbol: "OMR", region: "GCC" },
  { code: "AED", label: "UAE Dirham", symbol: "AED", region: "GCC" },
  { code: "SAR", label: "Saudi Riyal", symbol: "SAR", region: "GCC" },
  { code: "QAR", label: "Qatari Riyal", symbol: "QAR", region: "GCC" },
  { code: "BHD", label: "Bahraini Dinar", symbol: "BHD", region: "GCC" },
  { code: "KWD", label: "Kuwaiti Dinar", symbol: "KWD", region: "GCC" },
  { code: "EUR", label: "Euro", symbol: "€", region: "Europe" },
  { code: "GBP", label: "British Pound", symbol: "£", region: "Europe" },
  { code: "USD", label: "US Dollar", symbol: "$", region: "International" },
  { code: "CHF", label: "Swiss Franc", symbol: "CHF", region: "Europe" },
  { code: "TRY", label: "Turkish Lira", symbol: "₺", region: "Europe" }
] as const;
