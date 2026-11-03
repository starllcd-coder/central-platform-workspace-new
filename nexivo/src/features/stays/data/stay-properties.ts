import type { StayProperty } from "@/features/stays/types/stays.types";

export const stayProperties: StayProperty[] = [
  {
    id: "stay-001",
    name: "Salalah Garden Suites",
    slug: "salalah-garden-suites",
    type: "serviced-apartment",
    city: "Salalah",
    country: "Oman",
    area: "Al Haffa",
    rating: 4.7,
    reviewCount: 284,
    pricePerNight: 32,
    currency: "OMR",
    imageUrl: "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1400&auto=format&fit=crop",
    gallery: [
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1400&auto=format&fit=crop",
      "https://images.unsplash.com/photo-1571896349842-33c89424de2d?q=80&w=1400&auto=format&fit=crop"
    ],
    shortDescription: "Elegant serviced apartments close to beaches, gardens, and Khareef season attractions.",
    amenities: ["wifi", "parking", "family-rooms", "kitchen", "laundry"],
    featured: true,
    verified: true,
    payAtProperty: true,
    freeCancellation: true
  },
  {
    id: "stay-002",
    name: "Muscat Pearl Hotel",
    slug: "muscat-pearl-hotel",
    type: "hotel",
    city: "Muscat",
    country: "Oman",
    area: "Qurum",
    rating: 4.6,
    reviewCount: 421,
    pricePerNight: 48,
    currency: "OMR",
    imageUrl: "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=1400&auto=format&fit=crop",
    gallery: [
      "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=1400&auto=format&fit=crop"
    ],
    shortDescription: "Premium city hotel near beaches, business districts, shopping areas, and restaurants.",
    amenities: ["wifi", "parking", "pool", "breakfast", "gym"],
    featured: true,
    verified: true,
    payAtProperty: true,
    freeCancellation: true
  },
  {
    id: "stay-003",
    name: "Dubai Marina Skyline Residence",
    slug: "dubai-marina-skyline-residence",
    type: "apartment",
    city: "Dubai",
    country: "United Arab Emirates",
    area: "Dubai Marina",
    rating: 4.8,
    reviewCount: 612,
    pricePerNight: 410,
    currency: "AED",
    imageUrl: "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1400&auto=format&fit=crop",
    gallery: [
      "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1400&auto=format&fit=crop"
    ],
    shortDescription: "Luxury apartment with skyline views, marina access, and premium lifestyle amenities.",
    amenities: ["wifi", "parking", "pool", "gym", "kitchen"],
    featured: true,
    verified: true,
    payAtProperty: false,
    freeCancellation: true
  },
  {
    id: "stay-004",
    name: "Doha West Bay Executive Hotel",
    slug: "doha-west-bay-executive-hotel",
    type: "hotel",
    city: "Doha",
    country: "Qatar",
    area: "West Bay",
    rating: 4.5,
    reviewCount: 198,
    pricePerNight: 520,
    currency: "QAR",
    imageUrl: "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?q=80&w=1400&auto=format&fit=crop",
    gallery: [
      "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?q=80&w=1400&auto=format&fit=crop"
    ],
    shortDescription: "Business-focused hotel in West Bay with meeting facilities and city access.",
    amenities: ["wifi", "parking", "breakfast", "gym", "airport-transfer"],
    featured: false,
    verified: true,
    payAtProperty: true,
    freeCancellation: false
  },
  {
    id: "stay-005",
    name: "Riyadh Business Serviced Apartments",
    slug: "riyadh-business-serviced-apartments",
    type: "serviced-apartment",
    city: "Riyadh",
    country: "Saudi Arabia",
    area: "King Fahd Road",
    rating: 4.4,
    reviewCount: 174,
    pricePerNight: 430,
    currency: "SAR",
    imageUrl: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?q=80&w=1400&auto=format&fit=crop",
    gallery: [
      "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?q=80&w=1400&auto=format&fit=crop"
    ],
    shortDescription: "Serviced apartments designed for corporate travelers and long-stay guests.",
    amenities: ["wifi", "parking", "kitchen", "laundry", "gym"],
    featured: false,
    verified: true,
    payAtProperty: true,
    freeCancellation: true
  },
  {
    id: "stay-006",
    name: "Khasab Coastal Resort",
    slug: "khasab-coastal-resort",
    type: "resort",
    city: "Khasab",
    country: "Oman",
    area: "Coastal Area",
    rating: 4.3,
    reviewCount: 96,
    pricePerNight: 58,
    currency: "OMR",
    imageUrl: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?q=80&w=1400&auto=format&fit=crop",
    gallery: [
      "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?q=80&w=1400&auto=format&fit=crop"
    ],
    shortDescription: "Relaxed coastal resort experience for families, nature lovers, and weekend travelers.",
    amenities: ["wifi", "parking", "pool", "beach", "family-rooms"],
    featured: true,
    verified: true,
    payAtProperty: true,
    freeCancellation: false
  }
];
