import type {
  Coupon,
  LoyaltyTierInfo,
  Promotion,
  SponsoredPlacement
} from "@/features/growth/types/growth.types";

export const loyaltyTiers: LoyaltyTierInfo[] = [
  {
    tier: "bronze",
    title: "Bronze",
    requiredPoints: 0,
    multiplier: "1x",
    benefits: [
      "Earn points on stays, cars, and laundry",
      "Access basic coupons",
      "Save wishlist items",
      "Verified review rewards"
    ]
  },
  {
    tier: "silver",
    title: "Silver",
    requiredPoints: 1500,
    multiplier: "1.2x",
    benefits: [
      "Higher earning rate",
      "Priority coupon access",
      "Early promotion notifications",
      "Referral bonus boost"
    ]
  },
  {
    tier: "gold",
    title: "Gold",
    requiredPoints: 5000,
    multiplier: "1.5x",
    benefits: [
      "Premium offers",
      "Room and vehicle upgrade coupons",
      "Priority support",
      "Partner promotion access"
    ]
  },
  {
    tier: "platinum",
    title: "Platinum",
    requiredPoints: 12000,
    multiplier: "2x",
    benefits: [
      "Maximum reward earning",
      "Exclusive GCC travel deals",
      "VIP support",
      "Future Europe expansion benefits"
    ]
  }
];

export const coupons: Coupon[] = [
  {
    id: "coupon-001",
    code: "NEXIVO10",
    title: "10% off first booking",
    description: "Introductory coupon for first Nexivo marketplace booking.",
    type: "percentage",
    valueLabel: "10%",
    serviceScope: "all",
    expiryDate: "31 Dec 2026",
    active: true
  },
  {
    id: "coupon-002",
    code: "STAYLUX20",
    title: "StayLux launch saving",
    description: "Special promotional coupon for selected stays.",
    type: "fixed",
    valueLabel: "20 OMR",
    serviceScope: "stays",
    expiryDate: "30 Sep 2026",
    active: true
  },
  {
    id: "coupon-003",
    code: "DRIVEUP",
    title: "DriveSphere upgrade coupon",
    description: "Upgrade offer for selected car rental bookings.",
    type: "upgrade",
    valueLabel: "Upgrade",
    serviceScope: "cars",
    expiryDate: "30 Sep 2026",
    active: true
  },
  {
    id: "coupon-004",
    code: "LAUNDRYFREE",
    title: "Free laundry delivery",
    description: "Free delivery for selected Laundrex orders.",
    type: "free-delivery",
    valueLabel: "Free delivery",
    serviceScope: "laundry",
    expiryDate: "31 Aug 2026",
    active: true
  }
];

export const promotions: Promotion[] = [
  {
    id: "promo-001",
    title: "Salalah Khareef Travel Collection",
    description: "Featured stays, rental cars, and laundry services for Salalah season.",
    serviceScope: "stays",
    location: "Salalah, Oman",
    badge: "Seasonal",
    href: "/destinations/salalah",
    imageUrl: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop"
  },
  {
    id: "promo-002",
    title: "Airport Car Rental Deals",
    description: "Featured DriveSphere rental cars near major GCC airports.",
    serviceScope: "cars",
    location: "GCC Airports",
    badge: "Mobility",
    href: "/cars",
    imageUrl: "https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?q=80&w=1200&auto=format&fit=crop"
  },
  {
    id: "promo-003",
    title: "Hotel Guest Laundry Support",
    description: "Laundrex pickup and delivery services for travelers staying in apartments or hotels.",
    serviceScope: "laundry",
    location: "Selected Cities",
    badge: "Convenience",
    href: "/laundry",
    imageUrl: "https://images.unsplash.com/photo-1604335399105-a0c585fd81a1?q=80&w=1200&auto=format&fit=crop"
  }
];

export const sponsoredPlacements: SponsoredPlacement[] = [
  {
    id: "sp-001",
    title: "Homepage Featured Stay",
    businessName: "Available Slot",
    serviceScope: "stays",
    placement: "homepage",
    monthlyPriceLabel: "Custom",
    status: "available"
  },
  {
    id: "sp-002",
    title: "Search Top Car Rental",
    businessName: "Available Slot",
    serviceScope: "cars",
    placement: "search-top",
    monthlyPriceLabel: "Custom",
    status: "available"
  },
  {
    id: "sp-003",
    title: "Destination Laundry Promotion",
    businessName: "Available Slot",
    serviceScope: "laundry",
    placement: "destination-page",
    monthlyPriceLabel: "Custom",
    status: "available"
  }
];
