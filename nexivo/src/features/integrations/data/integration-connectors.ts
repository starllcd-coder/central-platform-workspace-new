import type { IntegrationConnector } from "@/features/integrations/types/integration.types";

export const integrationConnectors: IntegrationConnector[] = [
  {
    id: "conn-identity",
    name: "Central Identity",
    module: "identity",
    description: "Unified customer, partner, staff, and admin accounts across Nexivo and DSS products.",
    status: "mock",
    endpoint: "/api/central/identity",
    requiredForLaunch: true
  },
  {
    id: "conn-tenants",
    name: "Tenant Management",
    module: "tenants",
    description: "Business registration, module access, onboarding, country settings, and tenant separation.",
    status: "mock",
    endpoint: "/api/central/tenants",
    requiredForLaunch: true
  },
  {
    id: "conn-marketplace",
    name: "Marketplace Inventory",
    module: "marketplace",
    description: "StayLux properties, DriveSphere vehicles, Laundrex providers, destinations, and search visibility.",
    status: "mock",
    endpoint: "/api/central/marketplace",
    requiredForLaunch: true
  },
  {
    id: "conn-pricing",
    name: "Pricing Engine",
    module: "pricing",
    description: "Setup fees, commissions, subscriptions, coupons, promotions, sponsored listings, and custom contracts.",
    status: "mock",
    endpoint: "/api/central/pricing",
    requiredForLaunch: true
  },
  {
    id: "conn-payments",
    name: "Payment Gateway Layer",
    module: "payments",
    description: "Online payments, pay-at-property guarantees, pay-at-pickup guarantees, card tokenization, and refunds.",
    status: "planned",
    endpoint: "/api/central/payments",
    requiredForLaunch: true
  },
  {
    id: "conn-billing",
    name: "Business Billing",
    module: "billing",
    description: "Partner invoices, setup fee billing, subscriptions, commissions, settlement, and reconciliation.",
    status: "mock",
    endpoint: "/api/central/billing",
    requiredForLaunch: true
  },
  {
    id: "conn-notifications",
    name: "Notification Service",
    module: "notifications",
    description: "Email, SMS, WhatsApp, push templates, delivery logs, and customer preferences.",
    status: "mock",
    endpoint: "/api/central/notifications",
    requiredForLaunch: false
  },
  {
    id: "conn-analytics",
    name: "Analytics Warehouse",
    module: "analytics",
    description: "Marketplace views, bookings, revenue, funnels, partner performance, and business insights.",
    status: "mock",
    endpoint: "/api/central/analytics",
    requiredForLaunch: false
  },
  {
    id: "conn-privacy",
    name: "Privacy & Consent",
    module: "privacy",
    description: "Cookie consent, GDPR requests, data export, deletion, audit logs, and customer privacy controls.",
    status: "mock",
    endpoint: "/api/central/privacy",
    requiredForLaunch: false
  }
];
