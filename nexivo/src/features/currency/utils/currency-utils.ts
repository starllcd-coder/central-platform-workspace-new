import type { CurrencyCode } from "@/features/currency/types/currency.types";
import { currencies } from "@/features/currency/data/currencies";

export function getCurrencyInfo(code: CurrencyCode) {
  return currencies.find((currency) => currency.code === code) ?? currencies[0];
}

export function formatMoney(
  amount: number,
  currencyCode: CurrencyCode = "OMR",
  locale = "en"
): string {
  const currency = getCurrencyInfo(currencyCode);

  try {
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency: currency.code,
      minimumFractionDigits: currency.decimalPlaces,
      maximumFractionDigits: currency.decimalPlaces
    }).format(amount);
  } catch {
    return `${currency.symbol} ${amount.toFixed(currency.decimalPlaces)}`;
  }
}

export function getDefaultCurrencyByCountry(countryCode: string): CurrencyCode {
  const map: Record<string, CurrencyCode> = {
    OM: "OMR",
    AE: "AED",
    SA: "SAR",
    QA: "QAR",
    BH: "BHD",
    KW: "KWD",
    DE: "EUR",
    FR: "EUR",
    ES: "EUR",
    IT: "EUR",
    PT: "EUR",
    NL: "EUR",
    TR: "TRY",
    RU: "RUB",
    GB: "GBP",
    US: "USD"
  };

  return map[countryCode] ?? "OMR";
}
