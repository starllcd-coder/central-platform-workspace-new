import type { StayProperty, StaySearchFilters } from "@/features/stays/types/stays.types";
import { stayProperties } from "@/features/stays/data/stay-properties";

export function searchStayProperties(
  filters: Partial<StaySearchFilters>,
  source: StayProperty[] = stayProperties
): StayProperty[] {
  const destination = filters.destination?.trim().toLowerCase();

  return source.filter((property) => {
    const matchesDestination = destination
      ? property.city.toLowerCase().includes(destination) ||
        property.country.toLowerCase().includes(destination) ||
        property.area.toLowerCase().includes(destination) ||
        property.name.toLowerCase().includes(destination)
      : true;

    const matchesTypes =
      filters.propertyTypes && filters.propertyTypes.length > 0
        ? filters.propertyTypes.includes(property.type)
        : true;

    const matchesAmenities =
      filters.amenities && filters.amenities.length > 0
        ? filters.amenities.every((amenity) => property.amenities.includes(amenity))
        : true;

    const matchesPrice =
      typeof filters.minPrice === "number" || typeof filters.maxPrice === "number"
        ? property.pricePerNight >= (filters.minPrice ?? 0) &&
          property.pricePerNight <= (filters.maxPrice ?? Number.MAX_SAFE_INTEGER)
        : true;

    const matchesRating = filters.rating ? property.rating >= filters.rating : true;

    const matchesPayAtProperty =
      typeof filters.payAtProperty === "boolean"
        ? property.payAtProperty === filters.payAtProperty
        : true;

    const matchesFreeCancellation =
      typeof filters.freeCancellation === "boolean"
        ? property.freeCancellation === filters.freeCancellation
        : true;

    return (
      matchesDestination &&
      matchesTypes &&
      matchesAmenities &&
      matchesPrice &&
      matchesRating &&
      matchesPayAtProperty &&
      matchesFreeCancellation
    );
  });
}

export function getPropertyBySlug(slug: string): StayProperty | undefined {
  return stayProperties.find((property) => property.slug === slug);
}

export function getFeaturedProperties(): StayProperty[] {
  return stayProperties.filter((property) => property.featured);
}
