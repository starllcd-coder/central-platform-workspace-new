"use client";

import { MapPin } from "lucide-react";
import { countries } from "@/features/geo/data/countries";
import { allCities } from "@/features/geo/data/cities";
import { useGeoStore } from "@/features/geo/store/geo.store";
import type { CountryCode } from "@/features/geo/types/geo.types";
import { getCitiesByCountry, getCountryByCode } from "@/features/geo/utils/geo-utils";
import { useCurrencyStore } from "@/features/currency/store/currency.store";
import { getDefaultCurrencyByCountry } from "@/features/currency/utils/currency-utils";

export function RegionSelector() {
  const { countryCode, cityId, timezone, setCountryCode, setCityId, setTimezone } = useGeoStore();
  const { setCurrency, setSettlementCurrency } = useCurrencyStore();

  const cities = getCitiesByCountry(countryCode);
  const selectedCountry = getCountryByCode(countryCode);

  function handleCountryChange(nextCountryCode: CountryCode) {
    const country = getCountryByCode(nextCountryCode);
    const firstCity = allCities.find((city) => city.countryCode === nextCountryCode);

    setCountryCode(nextCountryCode);
    setTimezone(country.timezone);
    setCurrency(getDefaultCurrencyByCountry(nextCountryCode));
    setSettlementCurrency(getDefaultCurrencyByCountry(nextCountryCode));

    if (firstCity) {
      setCityId(firstCity.id);
    }
  }

  return (
    <div className="rounded-4xl border border-slate-200 bg-white p-5 shadow-premium">
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-50 text-brand-700">
          <MapPin size={20} />
        </div>

        <div>
          <h3 className="font-heading text-lg font-semibold text-luxury-ink">
            Region preferences
          </h3>
          <p className="text-sm text-slate-500">
            Country, city, timezone, and currency can be auto-detected but manually changed.
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <label className="space-y-2">
          <span className="text-sm font-semibold text-slate-700">Country</span>
          <select
            value={countryCode}
            onChange={(event) => handleCountryChange(event.target.value as CountryCode)}
            className="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm font-semibold shadow-sm"
          >
            {countries.map((country) => (
              <option key={country.code} value={country.code}>
                {country.name}
              </option>
            ))}
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-sm font-semibold text-slate-700">City</span>
          <select
            value={cityId}
            onChange={(event) => setCityId(event.target.value)}
            className="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm font-semibold shadow-sm"
          >
            {cities.map((city) => (
              <option key={city.id} value={city.id}>
                {city.name}
              </option>
            ))}
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-sm font-semibold text-slate-700">Timezone</span>
          <input
            value={timezone || selectedCountry.timezone}
            readOnly
            className="h-12 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm font-semibold text-slate-600 shadow-sm"
          />
        </label>
      </div>
    </div>
  );
}
