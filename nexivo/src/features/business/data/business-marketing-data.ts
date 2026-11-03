import {
  BarChart3,
  BedDouble,
  Building2,
  CalendarCheck2,
  Car,
  CreditCard,
  FileText,
  Globe2,
  Hotel,
  Layers3,
  LineChart,
  Megaphone,
  MessageCircle,
  ShieldCheck,
  Shirt,
  Smartphone,
  Sparkles,
  Users,
  WalletCards
} from "lucide-react";

export const businessHeroMetrics = [
  {
    label: "DSS Products",
    value: "4",
    description: "StayLux, DriveSphere, Laundrex, and DSS Central Platform."
  },
  {
    label: "Commercial Models",
    value: "3",
    description: "Setup fee, commission, and subscription."
  },
  {
    label: "Launch Region",
    value: "GCC",
    description: "Oman, UAE, Saudi Arabia, Qatar, Bahrain, and Kuwait."
  }
] as const;

export const dssProductCards = [
  {
    title: "Nexivo StayLux",
    href: "/business/staylux",
    icon: Hotel,
    badge: "Hotels & Properties",
    description:
      "Property management, accommodation booking, room inventory, owner portal, guest workflows, marketplace listing, and reporting.",
    highlights: ["Hotels", "Apartments", "Villas", "Owner Portal"],
    pricing: "From 200 OMR setup + flexible commission model"
  },
  {
    title: "Nexivo DriveSphere",
    href: "/business/drivesphere",
    icon: Car,
    badge: "Car Rental Companies",
    description:
      "Fleet management, rental bookings, branch operations, staff/admin app, customer booking app, payments, and reports.",
    highlights: ["Fleet", "Bookings", "Staff App", "Customer App"],
    pricing: "From 200 OMR setup + flexible booking commission"
  },
  {
    title: "Nexivo Laundrex",
    href: "/business/laundrex",
    icon: Shirt,
    badge: "Laundry Businesses",
    description:
      "Laundry order management, pickup and delivery workflow, branch operations, service catalog, customer app, and notifications.",
    highlights: ["Pickup", "Delivery", "Orders", "No Order Commission"],
    pricing: "From 200 OMR setup + subscription model"
  },
  {
    title: "DSS Central Platform",
    href: "/business/central-platform",
    icon: Layers3,
    badge: "Central Control",
    description:
      "Tenant management, pricing, commissions, subscriptions, billing, payments, analytics, marketplace controls, and integrations.",
    highlights: ["Tenants", "Pricing", "Billing", "Analytics"],
    pricing: "Centralized control for all DSS products"
  }
] as const;

export const stayLuxFeatures = [
  { title: "Property Management", description: "Hotels, apartments, villas, rooms, units, amenities, policies, and availability.", icon: BedDouble },
  { title: "Booking Engine", description: "Guest booking flow, pay online, pay at property, card guarantee, and booking confirmation.", icon: CalendarCheck2 },
  { title: "Owner Portal", description: "Owner monitoring, property performance, occupancy, revenue, and operational visibility.", icon: Users },
  { title: "Reports & Analytics", description: "Booking reports, revenue, occupancy, guest source, and marketplace performance.", icon: BarChart3 }
] as const;

export const driveSphereFeatures = [
  { title: "Fleet Management", description: "Vehicle inventory, availability, categories, pricing, branches, and rental workflows.", icon: Car },
  { title: "Admin & Staff Mobile App", description: "Same operational workflow as the web app for staff and admin teams.", icon: Smartphone },
  { title: "Rental Booking Flow", description: "Pickup, return, driver details, deposits, documents, card guarantee, and rental terms.", icon: CalendarCheck2 },
  { title: "Payments & Reports", description: "Online payments, pay-at-pickup options, revenue tracking, and partner billing.", icon: CreditCard }
] as const;

export const laundrexFeatures = [
  { title: "Order Management", description: "Pickup, delivery, wash, iron, dry cleaning, express service, and hotel guest orders.", icon: Shirt },
  { title: "Service Catalog", description: "Configurable services, pricing, estimated time, minimum order, and provider rules.", icon: FileText },
  { title: "Customer Updates", description: "Email, SMS, WhatsApp, and push notification readiness for order updates.", icon: MessageCircle },
  { title: "Subscription Model", description: "Laundrex is designed for setup plus subscription pricing, not per-order commission.", icon: WalletCards }
] as const;

export const centralPlatformFeatures = [
  { title: "Tenant Management", description: "Business registration, tenant modules, product access, onboarding, and account control.", icon: Building2 },
  { title: "Pricing Engine", description: "Setup fees, subscriptions, commissions, pricing versions, discounts, and custom contracts.", icon: WalletCards },
  { title: "Marketplace Management", description: "Listings, featured placements, sponsored search, banners, and destination campaigns.", icon: Megaphone },
  { title: "Security & Compliance", description: "Audit readiness, access control, privacy controls, GDPR preparation, and data protection.", icon: ShieldCheck },
  { title: "Multi-Country Readiness", description: "Countries, currencies, languages, taxes, regions, and Europe-ready expansion.", icon: Globe2 },
  { title: "Analytics & Reporting", description: "Marketplace performance, partner revenue, bookings, subscriptions, and business insights.", icon: LineChart }
] as const;

export const businessTrustItems = [
  {
    title: "Flexible pricing",
    description: "Do not expose exact commission percentages publicly. Discuss custom pricing after demo.",
    icon: WalletCards
  },
  {
    title: "Marketplace growth",
    description: "Businesses can gain visibility through Nexivo customer marketplace and future sponsored placement options.",
    icon: Sparkles
  },
  {
    title: "Centralized operations",
    description: "Pricing, billing, commissions, tenants, and modules stay configurable from DSS Central Platform.",
    icon: Layers3
  }
] as const;
