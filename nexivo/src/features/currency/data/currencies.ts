import type { CurrencyInfo } from "@/features/currency/types/currency.types";

export const currencies: CurrencyInfo[] = [
  {
    code: "OMR",
    name: "Omani Rial",
    symbol: "OMR",
    decimalPlaces: 3,
    region: "GCC",
    launchCurrency: true
  },
  {
    code: "AED",
    name: "UAE Dirham",
    symbol: "AED",
    decimalPlaces: 2,
    region: "GCC",
    launchCurrency: true
  },
  {
    code: "SAR",
    name: "Saudi Riyal",
    symbol: "SAR",
    decimalPlaces: 2,
    region: "GCC",
    launchCurrency: true
  },
  {
    code: "QAR",
    name: "Qatari Riyal",
    symbol: "QAR",
    decimalPlaces: 2,
    region: "GCC",
    launchCurrency: true
  },
  {
    code: "BHD",
    name: "Bahraini Dinar",
    symbol: "BHD",
    decimalPlaces: 3,
    region: "GCC",
    launchCurrency: true
  },
  {
    code: "KWD",
    name: "Kuwaiti Dinar",
    symbol: "KWD",
    decimalPlaces: 3,
    region: "GCC",
    launchCurrency: true
  },
  {
    code: "EUR",
    name: "Euro",
    symbol: "€",
    decimalPlaces: 2,
    region: "Europe",
    launchCurrency: false
  },
  {
    code: "GBP",
    name: "British Pound",
    symbol: "£",
    decimalPlaces: 2,
    region: "Europe",
    launchCurrency: false
  },
  {
    code: "USD",
    name: "US Dollar",
    symbol: "$",
    decimalPlaces: 2,
    region: "International",
    launchCurrency: false
  },
  {
    code: "CHF",
    name: "Swiss Franc",
    symbol: "CHF",
    decimalPlaces: 2,
    region: "Europe",
    launchCurrency: false
  },
  {
    code: "TRY",
    name: "Turkish Lira",
    symbol: "₺",
    decimalPlaces: 2,
    region: "Europe",
    launchCurrency: false
  },
  {
    code: "RUB",
    name: "Russian Ruble",
    symbol: "₽",
    decimalPlaces: 2,
    region: "Europe",
    launchCurrency: false
  }
];
