import type { CarSearchFilters, RentalVehicle } from "@/features/cars/types/cars.types";
import { rentalVehicles } from "@/features/cars/data/rental-vehicles";

export function searchRentalVehicles(
  filters: Partial<CarSearchFilters>,
  source: RentalVehicle[] = rentalVehicles
): RentalVehicle[] {
  const location = filters.location?.trim().toLowerCase();

  return source.filter((vehicle) => {
    const matchesLocation = location
      ? vehicle.city.toLowerCase().includes(location) ||
        vehicle.country.toLowerCase().includes(location) ||
        vehicle.pickupLocation.toLowerCase().includes(location) ||
        vehicle.companyName.toLowerCase().includes(location) ||
        vehicle.name.toLowerCase().includes(location)
      : true;

    const matchesCategory =
      filters.category && filters.category.length > 0
        ? filters.category.includes(vehicle.category)
        : true;

    const matchesFeatures =
      filters.features && filters.features.length > 0
        ? filters.features.every((feature) => vehicle.features.includes(feature))
        : true;

    const matchesPrice =
      typeof filters.minPrice === "number" || typeof filters.maxPrice === "number"
        ? vehicle.pricePerDay >= (filters.minPrice ?? 0) &&
          vehicle.pricePerDay <= (filters.maxPrice ?? Number.MAX_SAFE_INTEGER)
        : true;

    const matchesTransmission = filters.transmission
      ? vehicle.transmission === filters.transmission
      : true;

    const matchesFreeCancellation =
      typeof filters.freeCancellation === "boolean"
        ? vehicle.freeCancellation === filters.freeCancellation
        : true;

    const matchesPayAtPickup =
      typeof filters.payAtPickup === "boolean"
        ? vehicle.payAtPickup === filters.payAtPickup
        : true;

    return (
      matchesLocation &&
      matchesCategory &&
      matchesFeatures &&
      matchesPrice &&
      matchesTransmission &&
      matchesFreeCancellation &&
      matchesPayAtPickup
    );
  });
}

export function getVehicleBySlug(slug: string): RentalVehicle | undefined {
  return rentalVehicles.find((vehicle) => vehicle.slug === slug);
}

export function getFeaturedVehicles(): RentalVehicle[] {
  return rentalVehicles.filter((vehicle) => vehicle.featured);
}
