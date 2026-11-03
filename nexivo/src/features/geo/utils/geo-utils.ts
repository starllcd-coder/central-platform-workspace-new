import type { CountryCode } from "@/features/geo/types/geo.types";
import { allCities } from "@/features/geo/data/cities";
import { countries } from "@/features/geo/data/countries";
import { destinations } from "@/features/geo/data/destinations";

export function getCountryByCode(code: CountryCode) {
  return countries.find((country) => country.code === code) ?? countries[0];
}

export function getCitiesByCountry(countryCode: CountryCode) {
  return allCities
    .filter((city) => city.countryCode === countryCode)
    .sort((a, b) => b.priority - a.priority);
}

export function getFeaturedCities(limit = 12) {
  return [...allCities].sort((a, b) => b.priority - a.priority).slice(0, limit);
}

export function searchCities(query: string) {
  const normalized = query.trim().toLowerCase();

  if (!normalized) return getFeaturedCities();

  return allCities.filter((city) => {
    const country = getCountryByCode(city.countryCode);

    return (
      city.name.toLowerCase().includes(normalized) ||
      city.slug.includes(normalized) ||
      country.name.toLowerCase().includes(normalized) ||
      city.airportCodes?.some((airport) => airport.toLowerCase().includes(normalized))
    );
  });
}

export function getDestinationsByCity(cityId: string) {
  return destinations.filter((destination) => destination.cityId === cityId);
}
