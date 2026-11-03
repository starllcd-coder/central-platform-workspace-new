import type { PricingPlan } from "@/features/pricing/types/pricing.types";

export const pricingPlans: PricingPlan[] = [
  {
    id: "price-staylux",
    product: "staylux",
    productName: "StayLux",
    title: "Hotels, Apartments & Properties",
    setupFee: "From 200 OMR",
    ongoingModel: "Flexible commission-based model",
    publicDescription:
      "Designed for hotels, serviced apartments, villas, and property managers who want DSS software plus Nexivo marketplace visibility.",
    highlights: [
      "Property and room management",
      "Nexivo marketplace listing",
      "Booking engine",
      "Owner portal",
      "Reports and analytics",
      "Commission adjustable from Central Platform"
    ],
    recommendedFor: "Hotels, apartments, villas, and property managers",
    exactCommissionVisible: false
  },
  {
    id: "price-drivesphere",
    product: "drivesphere",
    productName: "DriveSphere",
    title: "Car Rental Companies",
    setupFee: "From 200 OMR",
    ongoingModel: "Flexible booking commission model",
    publicDescription:
      "Designed for car rental businesses that want fleet management, booking apps, staff workflows, and Nexivo customer demand.",
    highlights: [
      "Fleet and branch management",
      "Customer booking flow",
      "Admin/staff mobile workflow",
      "Driver documents",
      "Deposits and payment options",
      "Commission adjustable from Central Platform"
    ],
    recommendedFor: "Car rental companies and fleet operators",
    exactCommissionVisible: false
  },
  {
    id: "price-laundrex",
    product: "laundrex",
    productName: "Laundrex",
    title: "Laundry Businesses",
    setupFee: "From 200 OMR",
    ongoingModel: "Subscription-based model",
    publicDescription:
      "Designed for laundries that need pickup, delivery, order management, customer app, and predictable fixed platform cost.",
    highlights: [
      "Laundry service catalog",
      "Pickup and delivery workflow",
      "Customer order flow",
      "Branch operations",
      "Notifications",
      "No order commission required"
    ],
    recommendedFor: "Laundry shops and pickup/delivery laundry operators",
    exactCommissionVisible: false
  }
];

export const pricingFaqs = [
  {
    question: "Should exact commission percentages be shown publicly?",
    answer:
      "No. Nexivo should publicly show setup fees and commercial model type, but exact percentages should remain flexible and discussed after demo."
  },
  {
    question: "Can pricing and commissions change later?",
    answer:
      "Yes. Pricing, commission, subscription, setup fee, discounts, promotions, and featured listings should be configurable from DSS Central Platform."
  },
  {
    question: "Why does Laundrex use subscription instead of commission?",
    answer:
      "Laundry orders are often low-value and frequent. A fixed subscription is usually easier for operators to accept than per-order commission."
  },
  {
    question: "Is 200 OMR the final price?",
    answer:
      "No. It is a public starting setup fee. Final pricing depends on business size, modules, country, integration needs, and marketplace participation."
  }
] as const;
