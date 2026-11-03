"use client";

import { create } from "zustand";
import type { CountryCode } from "@/features/geo/types/geo.types";

type GeoStore = {
  countryCode: CountryCode;
  cityId: string;
  timezone: string;
  setCountryCode: (countryCode: CountryCode) => void;
  setCityId: (cityId: string) => void;
  setTimezone: (timezone: string) => void;
};

export const useGeoStore = create<GeoStore>((set) => ({
  countryCode: "OM",
  cityId: "om-salalah",
  timezone: "Asia/Muscat",

  setCountryCode: (countryCode) => set({ countryCode }),
  setCityId: (cityId) => set({ cityId }),
  setTimezone: (timezone) => set({ timezone })
}));
