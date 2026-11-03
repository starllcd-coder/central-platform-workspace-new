"use client";

import { ChevronDown, Globe2, WalletCards } from "lucide-react";
import { supportedLocales } from "@/features/localization/data/locales";
import { useLocalizationStore } from "@/features/localization/store/localization.store";
import type { SupportedLocale } from "@/features/localization/types/localization.types";
import { currencies } from "@/features/currency/data/currencies";
import { useCurrencyStore } from "@/features/currency/store/currency.store";
import type { CurrencyCode } from "@/features/currency/types/currency.types";

export function HeaderControls() {
  const { locale, setLocale } = useLocalizationStore();
  const { currency, setCurrency } = useCurrencyStore();

  return (
    <div className="flex items-center gap-2">
      <div className="group relative">
        <button className="inline-flex h-11 items-center gap-2 rounded-full border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 shadow-soft">
          <Globe2 size={16} />
          {locale.toUpperCase()}
          <ChevronDown size={14} />
        </button>

        <div className="invisible absolute right-0 top-12 w-64 translate-y-2 rounded-3xl border border-slate-200 bg-white p-2 opacity-0 shadow-premium transition-all group-hover:visible group-hover:translate-y-0 group-hover:opacity-100">
          {supportedLocales.map((item) => (
            <button
              key={item.code}
              onClick={() => setLocale(item.code as SupportedLocale)}
              className="flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left text-sm hover:bg-slate-50"
            >
              <span>
                <span className="block font-semibold text-slate-800">{item.nativeName}</span>
                <span className="text-xs text-slate-500">{item.englishName}</span>
              </span>
              <span className="uppercase text-slate-400">{item.code}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="group relative">
        <button className="inline-flex h-11 items-center gap-2 rounded-full border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 shadow-soft">
          <WalletCards size={16} />
          {currency}
          <ChevronDown size={14} />
        </button>

        <div className="invisible absolute right-0 top-12 w-72 translate-y-2 rounded-3xl border border-slate-200 bg-white p-2 opacity-0 shadow-premium transition-all group-hover:visible group-hover:translate-y-0 group-hover:opacity-100">
          {currencies.map((item) => (
            <button
              key={item.code}
              onClick={() => setCurrency(item.code as CurrencyCode)}
              className="flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left text-sm hover:bg-slate-50"
            >
              <span>
                <span className="block font-semibold text-slate-800">{item.code}</span>
                <span className="text-xs text-slate-500">{item.name}</span>
              </span>
              <span className="text-slate-500">{item.symbol}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
