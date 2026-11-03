export type LaundryServiceType =
  | "wash-fold"
  | "wash-iron"
  | "dry-cleaning"
  | "ironing"
  | "express"
  | "hotel-guest";

export type LaundryProviderFeature =
  | "pickup"
  | "delivery"
  | "same-day"
  | "hotel-pickup"
  | "eco-wash"
  | "card-payment"
  | "cash-payment"
  | "whatsapp-updates";

export type LaundryProvider = {
  id: string;
  name: string;
  slug: string;
  city: string;
  country: string;
  area: string;
  rating: number;
  reviewCount: number;
  minimumOrder: number;
  currency: "OMR" | "AED" | "SAR" | "QAR" | "BHD" | "KWD";
  imageUrl: string;
  shortDescription: string;
  serviceTypes: LaundryServiceType[];
  features: LaundryProviderFeature[];
  featured: boolean;
  verified: boolean;
  pickupAvailable: boolean;
  deliveryAvailable: boolean;
  providerResourceId?: string;
  providerResourceName?: string;
  providerResourceUnit?: "kg" | "piece" | "order";
};

export type LaundryServiceItem = {
  id: string;
  providerId: string;
  name: string;
  serviceType: LaundryServiceType;
  description: string;
  price: number;
  unit: "kg" | "piece" | "order";
  currency: LaundryProvider["currency"];
  estimatedTime: string;
};

export type LaundrySearchFilters = {
  location: string;
  serviceTypes: LaundryServiceType[];
  features: LaundryProviderFeature[];
  pickupDate: string;
  pickupAvailable?: boolean;
  deliveryAvailable?: boolean;
};

export type LaundryOrderDraft = {
  providerId: string;
  selectedItems: {
    serviceItemId: string;
    quantity: number;
  }[];
  pickupDate: string;
  pickupTime?: string;
  customerName?: string;
  customerEmail?: string;
  customerPhone?: string;
  pickupAddress?: string;
  deliveryAddress?: string;
  notes?: string;
  paymentMethod?: "pay-online" | "pay-on-delivery";
};
