"use client";

import { Check, Globe2 } from "lucide-react";
import { supportedLocales } from "@/features/localization/data/locales";
import { useLocalizationStore } from "@/features/localization/store/localization.store";
import type { SupportedLocale } from "@/features/localization/types/localization.types";
import { cn } from "@/lib/utils";

type LanguageSelectorProps = {
  compact?: boolean;
};

export function LanguageSelector({ compact = false }: LanguageSelectorProps) {
  const { locale, setLocale } = useLocalizationStore();

  if (compact) {
    return (
      <select
        value={locale}
        onChange={(event) => setLocale(event.target.value as SupportedLocale)}
        className="h-11 rounded-full border border-slate-200 bg-white px-4 text-sm font-semibold shadow-soft"
      >
        {supportedLocales.map((item) => (
          <option key={item.code} value={item.code}>
            {item.code.toUpperCase()}
          </option>
        ))}
      </select>
    );
  }

  return (
    <div className="rounded-4xl border border-slate-200 bg-white p-4 shadow-premium">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-50 text-brand-700">
          <Globe2 size={20} />
        </div>
        <div>
          <h3 className="font-heading text-lg font-semibold text-luxury-ink">Choose language</h3>
          <p className="text-sm text-slate-500">GCC launch and Europe-ready language support.</p>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {supportedLocales.map((item) => (
          <button
            key={item.code}
            type="button"
            onClick={() => setLocale(item.code)}
            className={cn(
              "flex items-center justify-between rounded-3xl border p-4 text-left transition-all",
              locale === item.code
                ? "border-brand-200 bg-brand-50 text-brand-800"
                : "border-slate-200 bg-white hover:bg-slate-50"
            )}
          >
            <span>
              <span className="block font-semibold">{item.nativeName}</span>
              <span className="mt-1 block text-xs text-slate-500">
                {item.englishName} • {item.region}
              </span>
            </span>

            {locale === item.code ? <Check size={18} /> : null}
          </button>
        ))}
      </div>
    </div>
  );
}
