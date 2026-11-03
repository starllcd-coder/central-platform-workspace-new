import {
  Building2,
  CalendarCheck2,
  Car,
  Hotel,
  MapPin,
  SearchCheck,
  Shirt,
  Sparkles,
  Star,
  Timer,
  WalletCards
} from "lucide-react";

export const featuredDestinationCards = [
  {
    city: "Salalah",
    country: "Oman",
    slug: "salalah",
    description: "Khareef season, beaches, mountains, family stays, rental cars, and laundry services.",
    highlights: ["Khareef", "Family Trips", "Nature"],
    stats: "120+ stays",
    imageGradient: "from-emerald-900 via-emerald-600 to-cyan-200",
    accent: "bg-emerald-500"
  },
  {
    city: "Muscat",
    country: "Oman",
    slug: "muscat",
    description: "Capital city stays, airport rentals, business travel, beaches, souqs, and cultural landmarks.",
    highlights: ["Business", "Culture", "Airport"],
    stats: "90+ stays",
    imageGradient: "from-slate-900 via-sky-700 to-luxury-dune",
    accent: "bg-sky-500"
  },
  {
    city: "Dubai",
    country: "United Arab Emirates",
    slug: "dubai",
    description: "Luxury hotels, apartments, car rentals, shopping, business travel, and lifestyle destinations.",
    highlights: ["Luxury", "Shopping", "Business"],
    stats: "300+ stays",
    imageGradient: "from-luxury-navy via-brand-700 to-luxury-gold",
    accent: "bg-luxury-gold"
  },
  {
    city: "Doha",
    country: "Qatar",
    slug: "doha",
    description: "Premium hotels, business districts, family stays, airport pickup, and city travel services.",
    highlights: ["Premium", "Business", "Family"],
    stats: "80+ stays",
    imageGradient: "from-[#3a1022] via-[#8a1538] to-[#e8d8bd]",
    accent: "bg-[#8a1538]"
  },
  {
    city: "Riyadh",
    country: "Saudi Arabia",
    slug: "riyadh",
    description: "Corporate stays, city mobility, fleet rentals, serviced apartments, and business travel.",
    highlights: ["Corporate", "Mobility", "Events"],
    stats: "140+ stays",
    imageGradient: "from-[#06351e] via-[#006c35] to-luxury-dune",
    accent: "bg-[#006c35]"
  },
  {
    city: "Kuwait City",
    country: "Kuwait",
    slug: "kuwait-city",
    description: "Hotels, apartments, rentals, business districts, shopping areas, and city services.",
    highlights: ["City", "Shopping", "Business"],
    stats: "70+ stays",
    imageGradient: "from-slate-950 via-slate-700 to-emerald-300",
    accent: "bg-slate-700"
  }
] as const;

export const marketplacePreviewCards = [
  {
    title: "StayLux Stays",
    action: "Book a Stay",
    description: "Hotels, apartments, villas, serviced residences, property galleries, reviews, policies, and booking flows.",
    href: "/stays",
    icon: Hotel,
    badge: "Accommodation",
    metrics: "Hotels • Apartments • Villas",
    tone: "from-luxury-navy via-brand-700 to-sky-500",
    features: ["Verified stays", "Flexible search", "Guest-ready policies"]
  },
  {
    title: "DriveSphere Cars",
    action: "Rent a Car",
    description: "Economy, SUV, luxury, airport pickup, branch pickup, fleet availability, driver details, and rental workflows.",
    href: "/cars",
    icon: Car,
    badge: "Car Rental",
    metrics: "Airport • City • Fleet",
    tone: "from-slate-950 via-slate-700 to-luxury-bronze",
    features: ["Airport pickup", "City branches", "Fleet availability"]
  },
  {
    title: "Laundrex Laundry",
    action: "Order Laundry",
    description: "Pickup scheduling, wash and press, delivery, hotel guest laundry, customer orders, and service catalog.",
    href: "/laundry",
    icon: Shirt,
    badge: "Laundry Services",
    metrics: "Pickup • Delivery • Tracking",
    tone: "from-emerald-950 via-emerald-700 to-luxury-gold",
    features: ["Pickup scheduling", "Wash and press", "Delivery tracking"]
  }
] as const;

export const marketplaceTrustItems = [
  {
    title: "Verified Business Listings",
    description: "Designed for verified hotels, car rental companies, and laundry providers across GCC destinations.",
    icon: Star
  },
  {
    title: "Destination-Based Discovery",
    description: "Customers can search by city, airport, area, tourist season, and service type.",
    icon: MapPin
  },
  {
    title: "Fast Booking Paths",
    description: "Service-specific flows make stays, cars, and laundry clear from the first click.",
    icon: SearchCheck
  },
  {
    title: "Operational Readiness",
    description: "Nexivo stays connected to DSS software concepts for pricing, tenants, reporting, and controls.",
    icon: Building2
  }
] as const;

export const dssTrustBadges = [
  { label: "DSS Central Platform", icon: Building2 },
  { label: "Dynamic pricing", icon: WalletCards },
  { label: "Multi-tenant SaaS", icon: Sparkles },
  { label: "GCC-first", icon: MapPin },
  { label: "Europe-ready", icon: CalendarCheck2 },
  { label: "Operational reporting", icon: Timer }
] as const;
