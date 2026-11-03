import type { StayRoom } from "@/features/stays/types/stay-booking.types";

export const stayRooms: StayRoom[] = [
  {
    id: "room-001",
    propertyId: "stay-001",
    name: "Garden Studio Suite",
    slug: "garden-studio-suite",
    description: "Modern studio suite with kitchenette, seating area, and garden-facing balcony.",
    maxGuests: 2,
    bedType: "1 King Bed",
    size: "42 sqm",
    pricePerNight: 32,
    currency: "OMR",
    refundable: true,
    breakfastIncluded: false,
    availableUnits: 5,
    imageUrl: "https://images.unsplash.com/photo-1590490360182-c33d57733427?q=80&w=1400&auto=format&fit=crop"
  },
  {
    id: "room-002",
    propertyId: "stay-001",
    name: "Family Apartment",
    slug: "family-apartment",
    description: "Two-bedroom serviced apartment suitable for families visiting Salalah.",
    maxGuests: 5,
    bedType: "1 King Bed + 2 Single Beds",
    size: "86 sqm",
    pricePerNight: 58,
    currency: "OMR",
    refundable: true,
    breakfastIncluded: false,
    availableUnits: 3,
    imageUrl: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=1400&auto=format&fit=crop"
  },
  {
    id: "room-003",
    propertyId: "stay-002",
    name: "Deluxe City Room",
    slug: "deluxe-city-room",
    description: "Elegant hotel room with city view, breakfast option, and business-friendly workspace.",
    maxGuests: 2,
    bedType: "1 King Bed",
    size: "34 sqm",
    pricePerNight: 48,
    currency: "OMR",
    refundable: true,
    breakfastIncluded: true,
    availableUnits: 8,
    imageUrl: "https://images.unsplash.com/photo-1591088398332-8a7791972843?q=80&w=1400&auto=format&fit=crop"
  },
  {
    id: "room-004",
    propertyId: "stay-003",
    name: "Marina One Bedroom Apartment",
    slug: "marina-one-bedroom-apartment",
    description: "Luxury one-bedroom apartment with marina views and premium building amenities.",
    maxGuests: 3,
    bedType: "1 King Bed + Sofa Bed",
    size: "74 sqm",
    pricePerNight: 410,
    currency: "AED",
    refundable: true,
    breakfastIncluded: false,
    availableUnits: 4,
    imageUrl: "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?q=80&w=1400&auto=format&fit=crop"
  },
  {
    id: "room-005",
    propertyId: "stay-004",
    name: "Executive King Room",
    slug: "executive-king-room",
    description: "Business room in West Bay with workspace, premium bedding, and optional breakfast.",
    maxGuests: 2,
    bedType: "1 King Bed",
    size: "38 sqm",
    pricePerNight: 520,
    currency: "QAR",
    refundable: false,
    breakfastIncluded: true,
    availableUnits: 6,
    imageUrl: "https://images.unsplash.com/photo-1611892440504-42a792e24d32?q=80&w=1400&auto=format&fit=crop"
  },
  {
    id: "room-006",
    propertyId: "stay-005",
    name: "Corporate One Bedroom Suite",
    slug: "corporate-one-bedroom-suite",
    description: "Long-stay business suite with kitchen, work desk, and laundry support.",
    maxGuests: 2,
    bedType: "1 Queen Bed",
    size: "58 sqm",
    pricePerNight: 430,
    currency: "SAR",
    refundable: true,
    breakfastIncluded: false,
    availableUnits: 7,
    imageUrl: "https://images.unsplash.com/photo-1600210492493-0946911123ea?q=80&w=1400&auto=format&fit=crop"
  },
  {
    id: "room-007",
    propertyId: "stay-006",
    name: "Coastal Resort Room",
    slug: "coastal-resort-room",
    description: "Relaxed resort room near coastal activities and family leisure areas.",
    maxGuests: 3,
    bedType: "1 King Bed + Sofa Bed",
    size: "44 sqm",
    pricePerNight: 58,
    currency: "OMR",
    refundable: false,
    breakfastIncluded: true,
    availableUnits: 4,
    imageUrl: "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?q=80&w=1400&auto=format&fit=crop"
  }
];

export function getRoomsByPropertyId(propertyId: string): StayRoom[] {
  return stayRooms.filter((room) => room.propertyId === propertyId);
}

export function getRoomById(roomId: string): StayRoom | undefined {
  return stayRooms.find((room) => room.id === roomId);
}
