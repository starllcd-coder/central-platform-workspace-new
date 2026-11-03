export type VehicleCategory =
  | "economy"
  | "compact"
  | "sedan"
  | "suv"
  | "luxury"
  | "van"
  | "pickup";

export type VehicleFeature =
  | "automatic"
  | "manual"
  | "air-conditioning"
  | "bluetooth"
  | "gps"
  | "child-seat"
  | "full-insurance"
  | "airport-pickup"
  | "unlimited-mileage"
  | "delivery";

export type RentalVehicle = {
  id: string;
  name: string;
  slug: string;
  companyName: string;
  category: VehicleCategory;
  city: string;
  country: string;
  pickupLocation: string;
  rating: number;
  reviewCount: number;
  pricePerDay: number;
  depositAmount: number;
  currency: "OMR" | "AED" | "SAR" | "QAR" | "BHD" | "KWD";
  imageUrl: string;
  shortDescription: string;
  seats: number;
  bags: number;
  transmission: "automatic" | "manual";
  fuelType: "petrol" | "diesel" | "hybrid" | "electric";
  features: VehicleFeature[];
  featured: boolean;
  verified: boolean;
  payOnline: boolean;
  payAtPickup: boolean;
  freeCancellation: boolean;
  providerResourceId?: string;
};

export type CarSearchFilters = {
  location: string;
  pickupDate: string;
  returnDate: string;
  category: VehicleCategory[];
  features: VehicleFeature[];
  minPrice?: number;
  maxPrice?: number;
  transmission?: "automatic" | "manual";
  freeCancellation?: boolean;
  payAtPickup?: boolean;
};
