import { centralPlatformFallbackEnabled, centralPlatformRequest, type CentralListResponse } from "@/lib/integrations/central-platform-api";
import { stayProperties } from "@/features/stays/data/stay-properties";
import { rentalVehicles } from "@/features/cars/data/rental-vehicles";
import { laundryProviders } from "@/features/laundry/data/laundry-providers";
import type { StayProperty } from "@/features/stays/types/stays.types";
import type { RentalVehicle } from "@/features/cars/types/cars.types";
import type { LaundryProvider } from "@/features/laundry/types/laundry.types";

type CentralListing = {
  id: number;
  resource?: { city?: string; country?: string; capacity?: number; seats?: number; transmission?: string; fuelType?: string; deposit?: string };
  listing_slug: string;
  tenant_name: string;
  tenant_country: string;
  image_url: string;
  module_code: string;
  provider_resource_id: string;
  provider_resource_name: string;
  provider_resource_unit: string;
  base_price: string;
  average_rating: string;
  rating_count: number;
  currency: StayProperty["currency"];
};

async function fetchListings(moduleCode: string) {
  try {
    const listings: CentralListing[] = [];
    let offset: number | null = 0;
    for (let page=0; offset !== null && page<100; page++) {
      const response: CentralListResponse<CentralListing> & { nextOffset?: number | null } = await centralPlatformRequest(
        `/listings/?module=${moduleCode}&offset=${offset}`
      );
      listings.push(...response.results);
      offset = typeof response.nextOffset === "number" && response.nextOffset > offset ? response.nextOffset : null;
    }
    return listings;
  } catch {
    if (!centralPlatformFallbackEnabled()) {
      throw new Error("Central Platform listings are unavailable.");
    }
    return [];
  }
}

export async function getCentralStayProperties(): Promise<StayProperty[]> {
  const listings = await fetchListings("staylux");
  if (listings.length === 0) return centralPlatformFallbackEnabled() ? stayProperties : [];

  return listings.map((listing, index) => ({
    id: `central-stay-${listing.id}`,
    name: listing.provider_resource_name || listing.tenant_name,
    slug: listing.listing_slug,
    type: "hotel",
    city: listing.resource?.city || listing.tenant_country || "",
    country: listing.resource?.country || listing.tenant_country || "",
    area: "Verified Partner",
    rating: Number(listing.average_rating) || 0,
    reviewCount: listing.rating_count,
    pricePerNight: Number(listing.base_price) || 0,
    currency: listing.currency,
    imageUrl: listing.image_url || "/icons/icon-512.svg",
    gallery: [],
    shortDescription: "Verified StayLux property synced from DSS Central Platform marketplace inventory.",
    amenities: [],
    featured: index === 0,
    verified: true,
    payAtProperty: true,
    freeCancellation: false,
    providerResourceId: listing.provider_resource_id,
    providerResourceName: listing.provider_resource_name || listing.tenant_name
  }));
}

export async function getCentralRentalVehicles(): Promise<RentalVehicle[]> {
  const listings = await fetchListings("drivesphere");
  if (listings.length === 0) return centralPlatformFallbackEnabled() ? rentalVehicles : [];

  return listings.map((listing, index) => ({
    id: `central-car-${listing.id}`,
    name: listing.provider_resource_name || `${listing.tenant_name} Fleet`,
    slug: listing.listing_slug,
    companyName: listing.tenant_name,
    category: "sedan",
    city: listing.resource?.city || listing.tenant_country || "",
    country: listing.resource?.country || listing.tenant_country || "",
    pickupLocation: "Verified Partner Branch",
    rating: Number(listing.average_rating) || 0,
    reviewCount: listing.rating_count,
    pricePerDay: Number(listing.base_price) || 0,
    depositAmount: Number(listing.resource?.deposit) || 0,
    currency: listing.currency,
    imageUrl: listing.image_url || "/icons/icon-512.svg",
    shortDescription: "Verified DriveSphere rental partner synced from DSS Central Platform marketplace inventory.",
    seats: listing.resource?.seats || 5,
    bags: 2,
    transmission: listing.resource?.transmission === "manual" ? "manual" : "automatic",
    fuelType: "petrol",
    features: [],
    featured: index === 0,
    verified: true,
    payOnline: false,
    payAtPickup: true,
    freeCancellation: false,
    providerResourceId: listing.provider_resource_id
  }));
}

export async function getCentralLaundryProviders(): Promise<LaundryProvider[]> {
  const listings = await fetchListings("laundrex");
  if (listings.length === 0) return centralPlatformFallbackEnabled() ? laundryProviders : [];

  return listings.map((listing, index) => ({
    id: `central-laundry-${listing.id}`,
    name: listing.tenant_name,
    slug: listing.listing_slug,
    city: listing.resource?.city || listing.tenant_country || "",
    country: listing.resource?.country || listing.tenant_country || "",
    area: "Verified Partner",
    rating: Number(listing.average_rating) || 0,
    reviewCount: listing.rating_count,
    minimumOrder: Number(listing.base_price) || 0,
    currency: listing.currency,
    imageUrl: listing.image_url || "/icons/icon-512.svg",
    shortDescription: "Verified Laundrex laundry partner synced from DSS Central Platform marketplace inventory.",
    serviceTypes: [],
    features: [],
    featured: index === 0,
    verified: true,
    pickupAvailable: true,
    deliveryAvailable: true,
    providerResourceId: listing.provider_resource_id,
    providerResourceName: listing.provider_resource_name || "Laundry service",
    providerResourceUnit: (["kg", "piece", "order"].includes(listing.provider_resource_unit)
      ? listing.provider_resource_unit
      : "order") as LaundryProvider["providerResourceUnit"]
  }));
}
