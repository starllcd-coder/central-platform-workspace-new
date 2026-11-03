import type { StayProperty } from "@/features/stays/types/stays.types";

export type StayRoom = {
  id: string;
  propertyId: string;
  name: string;
  slug: string;
  description: string;
  maxGuests: number;
  bedType: string;
  size: string;
  pricePerNight: number;
  currency: StayProperty["currency"];
  refundable: boolean;
  breakfastIncluded: boolean;
  availableUnits: number;
  imageUrl: string;
};

export type StayBookingDraft = {
  propertyId: string;
  roomId: string;
  checkIn: string;
  checkOut: string;
  guests: number;
  nights: number;
  customerName?: string;
  customerEmail?: string;
  customerPhone?: string;
  paymentMethod?: "pay-online" | "pay-at-property";
  cardGuaranteeRequired?: boolean;
};
