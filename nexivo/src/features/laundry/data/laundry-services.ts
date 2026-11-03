import type { LaundryServiceItem } from "@/features/laundry/types/laundry.types";

export const laundryServiceItems: LaundryServiceItem[] = [
  {
    id: "svc-001",
    providerId: "laundry-001",
    name: "Wash & Fold",
    serviceType: "wash-fold",
    description: "Daily clothes washed, dried, and folded.",
    price: 1.2,
    unit: "kg",
    currency: "OMR",
    estimatedTime: "24 hours"
  },
  {
    id: "svc-002",
    providerId: "laundry-001",
    name: "Wash & Iron",
    serviceType: "wash-iron",
    description: "Clothes washed, dried, and professionally ironed.",
    price: 1.6,
    unit: "kg",
    currency: "OMR",
    estimatedTime: "24-36 hours"
  },
  {
    id: "svc-003",
    providerId: "laundry-001",
    name: "Express Laundry",
    serviceType: "express",
    description: "Priority wash service for urgent orders.",
    price: 2.4,
    unit: "kg",
    currency: "OMR",
    estimatedTime: "Same day"
  },
  {
    id: "svc-004",
    providerId: "laundry-002",
    name: "Dry Cleaning",
    serviceType: "dry-cleaning",
    description: "Dry cleaning for formal wear and delicate garments.",
    price: 2.5,
    unit: "piece",
    currency: "OMR",
    estimatedTime: "48 hours"
  },
  {
    id: "svc-005",
    providerId: "laundry-003",
    name: "Wash & Fold",
    serviceType: "wash-fold",
    description: "Apartment and hotel guest laundry by kilogram.",
    price: 12,
    unit: "kg",
    currency: "AED",
    estimatedTime: "24 hours"
  },
  {
    id: "svc-006",
    providerId: "laundry-003",
    name: "Hotel Guest Express",
    serviceType: "hotel-guest",
    description: "Express pickup and delivery for hotel guests.",
    price: 45,
    unit: "order",
    currency: "AED",
    estimatedTime: "Same day"
  },
  {
    id: "svc-007",
    providerId: "laundry-004",
    name: "Executive Ironing",
    serviceType: "ironing",
    description: "Professional ironing for business clothing.",
    price: 8,
    unit: "piece",
    currency: "QAR",
    estimatedTime: "24 hours"
  }
];

export function getLaundryServicesByProvider(providerId: string): LaundryServiceItem[] {
  return laundryServiceItems.filter((item) => item.providerId === providerId);
}

export function getLaundryServiceById(serviceItemId: string): LaundryServiceItem | undefined {
  return laundryServiceItems.find((item) => item.id === serviceItemId);
}
