import {
  BriefcaseBusiness,
  Building2,
  CalendarCheck2,
  Car,
  Hotel,
  Landmark,
  Map,
  Shirt,
  Sparkles,
  Store,
  WalletCards,
  Waves
} from "lucide-react";

export const mainNavigation = [
  { label: "Stays", href: "/stays", description: "Hotels, apartments, villas, and rooms.", icon: Hotel },
  { label: "Cars", href: "/cars", description: "Rental vehicles with flexible pickup options.", icon: Car },
  { label: "Laundry", href: "/laundry", description: "Pickup, cleaning, ironing, and delivery.", icon: Shirt },
  { label: "Destinations", href: "/destinations", description: "Explore trips, places, and local experiences.", icon: Map },
  { label: "Business", href: "/business", description: "Software for hospitality, mobility, and services.", icon: Building2 },
  { label: "Pricing", href: "/pricing", description: "Plans for marketplace partners and operators.", icon: WalletCards }
] as const;

export const businessNavigation = [
  { label: "Business Home", href: "/business", description: "The Nexivo operating system for partners.", icon: BriefcaseBusiness },
  { label: "StayLux", href: "/business/staylux", description: "Property and booking tools for stay providers.", icon: Landmark },
  { label: "DriveSphere", href: "/business/drivesphere", description: "Fleet, rental, and branch management.", icon: Waves },
  { label: "Laundrex", href: "/business/laundrex", description: "Laundry order, catalog, and delivery workflows.", icon: Sparkles },
  {
    label: "Central Platform",
    href: "/business/central-platform",
    description: "Tenant, pricing, reporting, and marketplace controls.",
    icon: Store
  },
  { label: "Request Demo", href: "/business/request-demo", description: "Talk with the Nexivo team about your rollout.", icon: CalendarCheck2 }
] as const;

export const footerNavigation = [
  {
    title: "Marketplace",
    links: [
      { label: "Stays", href: "/stays" },
      { label: "Cars", href: "/cars" },
      { label: "Laundry", href: "/laundry" },
      { label: "Destinations", href: "/destinations" },
      { label: "Promotions", href: "/promotions" }
    ]
  },
  {
    title: "Business",
    links: businessNavigation
  },
  {
    title: "Support",
    links: [
      { label: "Contact", href: "/contact" },
      { label: "Support", href: "/support" },
      { label: "Security", href: "/security" },
      { label: "Notifications", href: "/notifications" },
      { label: "Integrations", href: "/integrations" }
    ]
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy", href: "/privacy" },
      { label: "GDPR", href: "/privacy/gdpr" },
      { label: "Cookie Center", href: "/cookie-center" },
      { label: "Terms", href: "/terms" },
      { label: "Data Requests", href: "/data-requests" }
    ]
  }
] as const;
