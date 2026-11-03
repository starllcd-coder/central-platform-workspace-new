"use client";

import { create } from "zustand";
import type { CurrencyCode } from "@/features/currency/types/currency.types";

type CurrencyStore = {
  currency: CurrencyCode;
  settlementCurrency: CurrencyCode;
  setCurrency: (currency: CurrencyCode) => void;
  setSettlementCurrency: (currency: CurrencyCode) => void;
};

export const useCurrencyStore = create<CurrencyStore>((set) => ({
  currency: "OMR",
  settlementCurrency: "OMR",

  setCurrency: (currency) => set({ currency }),
  setSettlementCurrency: (settlementCurrency) => set({ settlementCurrency })
}));
