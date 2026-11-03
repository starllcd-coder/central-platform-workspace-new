export type PropertyType =
  | "hotel"
  | "apartment"
  | "villa"
  | "serviced-apartment"
  | "resort";

export type PropertyAmenity =
  | "wifi"
  | "parking"
  | "pool"
  | "breakfast"
  | "gym"
  | "beach"
  | "airport-transfer"
  | "family-rooms"
  | "kitchen"
  | "laundry";

export type StayProperty = {
  id: string;
  name: string;
  slug: string;
  type: PropertyType;
  city: string;
  country: string;
  area: string;
  rating: number;
  reviewCount: number;
  pricePerNight: number;
  currency: "OMR" | "AED" | "SAR" | "QAR" | "BHD" | "KWD";
  imageUrl: string;
  gallery: string[];
  shortDescription: string;
  amenities: PropertyAmenity[];
  featured: boolean;
  verified: boolean;
  payAtProperty: boolean;
  freeCancellation: boolean;
  providerResourceId?: string;
  providerResourceName?: string;
};

export type StaySearchFilters = {
  destination: string;
  checkIn: string;
  checkOut: string;
  guests: number;
  propertyTypes: PropertyType[];
  amenities: PropertyAmenity[];
  minPrice?: number;
  maxPrice?: number;
  rating?: number;
  payAtProperty?: boolean;
  freeCancellation?: boolean;
};
