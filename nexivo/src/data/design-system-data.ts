import {
  Building2,
  Car,
  Globe2,
  Hotel,
  Languages,
  ShieldCheck,
  Shirt,
  Sparkles,
  WalletCards
} from "lucide-react";

export const platformHighlights = [
  {
    title: "StayLux",
    description: "Accommodation booking, property management, owner portal, and marketplace listings.",
    icon: Hotel,
    tone: "blue"
  },
  {
    title: "DriveSphere",
    description: "Vehicle search, fleet workflows, rental booking, staff apps, and partner operations.",
    icon: Car,
    tone: "dark"
  },
  {
    title: "Laundrex",
    description: "Laundry pickup, service catalog, customer order flow, and branch operations.",
    icon: Shirt,
    tone: "gold"
  },
  {
    title: "DSS Central Platform",
    description: "Pricing, commissions, tenants, billing, analytics, subscriptions, and marketplace control.",
    icon: Building2,
    tone: "green"
  }
] as const;

export const designPrinciples = [
  {
    title: "Modern & Elegant",
    description: "Premium travel marketplace interface with clean spacing, refined cards, and smooth motion.",
    icon: Sparkles
  },
  {
    title: "GCC First",
    description: "Built around GCC cities, currencies, Arabic/English support, and regional travel demand.",
    icon: Globe2
  },
  {
    title: "Europe Ready",
    description: "Prepared for European languages, GDPR controls, multi-currency, and international expansion.",
    icon: Languages
  },
  {
    title: "Secure by Design",
    description: "Designed for safe accounts, bookings, payments, document vault, and partner data separation.",
    icon: ShieldCheck
  },
  {
    title: "Dynamic Pricing",
    description: "Setup fees, commissions, subscriptions, promotions, and pricing plans controlled centrally.",
    icon: WalletCards
  }
] as const;
