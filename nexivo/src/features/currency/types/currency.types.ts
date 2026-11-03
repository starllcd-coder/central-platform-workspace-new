export type CurrencyCode =
  | "OMR"
  | "AED"
  | "SAR"
  | "QAR"
  | "BHD"
  | "KWD"
  | "EUR"
  | "GBP"
  | "USD"
  | "CHF"
  | "TRY"
  | "RUB";

export type CurrencyInfo = {
  code: CurrencyCode;
  name: string;
  symbol: string;
  decimalPlaces: number;
  region: "GCC" | "Europe" | "International";
  launchCurrency: boolean;
};
