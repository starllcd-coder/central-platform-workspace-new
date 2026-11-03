import { laundryProviders } from "@/features/laundry/data/laundry-providers";
import type { LaundryProvider, LaundrySearchFilters } from "@/features/laundry/types/laundry.types";

export function searchLaundryProviders(
  filters: Partial<LaundrySearchFilters>,
  source: LaundryProvider[] = laundryProviders
): LaundryProvider[] {
  const location = filters.location?.trim().toLowerCase();

  return source.filter((provider) => {
    const matchesLocation = location
      ? provider.city.toLowerCase().includes(location) ||
        provider.country.toLowerCase().includes(location) ||
        provider.area.toLowerCase().includes(location) ||
        provider.name.toLowerCase().includes(location)
      : true;

    const matchesServiceTypes =
      filters.serviceTypes && filters.serviceTypes.length > 0
        ? filters.serviceTypes.some((serviceType) => provider.serviceTypes.includes(serviceType))
        : true;

    const matchesFeatures =
      filters.features && filters.features.length > 0
        ? filters.features.every((feature) => provider.features.includes(feature))
        : true;

    const matchesPickup =
      typeof filters.pickupAvailable === "boolean"
        ? provider.pickupAvailable === filters.pickupAvailable
        : true;

    const matchesDelivery =
      typeof filters.deliveryAvailable === "boolean"
        ? provider.deliveryAvailable === filters.deliveryAvailable
        : true;

    return matchesLocation && matchesServiceTypes && matchesFeatures && matchesPickup && matchesDelivery;
  });
}

export function getLaundryProviderBySlug(slug: string): LaundryProvider | undefined {
  return laundryProviders.find((provider) => provider.slug === slug);
}

export function getFeaturedLaundryProviders(): LaundryProvider[] {
  return laundryProviders.filter((provider) => provider.featured);
}
