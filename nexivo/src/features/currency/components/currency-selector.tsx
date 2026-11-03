"use client";

import { Check, WalletCards } from "lucide-react";
import { currencies } from "@/features/currency/data/currencies";
import { useCurrencyStore } from "@/features/currency/store/currency.store";
import type { CurrencyCode } from "@/features/currency/types/currency.types";
import { cn } from "@/lib/utils";

type CurrencySelectorProps = {
  compact?: boolean;
};

export function CurrencySelector({ compact = false }: CurrencySelectorProps) {
  const { currency, setCurrency } = useCurrencyStore();

  if (compact) {
    return (
      <select
        value={currency}
        onChange={(event) => setCurrency(event.target.value as CurrencyCode)}
        className="h-11 rounded-full border border-slate-200 bg-white px-4 text-sm font-semibold shadow-soft"
      >
        {currencies.map((item) => (
          <option key={item.code} value={item.code}>
            {item.code}
          </option>
        ))}
      </select>
    );
  }

  return (
    <div className="rounded-4xl border border-slate-200 bg-white p-4 shadow-premium">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-luxury-gold/15 text-luxury-bronze">
          <WalletCards size={20} />
        </div>
        <div>
          <h3 className="font-heading text-lg font-semibold text-luxury-ink">Choose currency</h3>
          <p className="text-sm text-slate-500">
            Customer display currency can be different from business settlement currency.
          </p>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {currencies.map((item) => (
          <button
            key={item.code}
            type="button"
            onClick={() => setCurrency(item.code)}
            className={cn(
              "flex items-center justify-between rounded-3xl border p-4 text-left transition-all",
              currency === item.code
                ? "border-brand-200 bg-brand-50 text-brand-800"
                : "border-slate-200 bg-white hover:bg-slate-50"
            )}
          >
            <span>
              <span className="block font-semibold">{item.code}</span>
              <span className="mt-1 block text-xs text-slate-500">
                {item.name} • {item.region}
              </span>
            </span>

            <span className="flex items-center gap-2">
              <span className="text-sm text-slate-500">{item.symbol}</span>
              {currency === item.code ? <Check size={18} /> : null}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
