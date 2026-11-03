import type {
  ConsentPreference,
  DataRequest,
  SecurityControl
} from "@/features/privacy/types/privacy.types";

export const defaultConsentPreferences: ConsentPreference[] = [
  {
    category: "strictly-necessary",
    title: "Strictly Necessary Cookies",
    description:
      "Required for login, booking flow, security, language, currency, and basic platform functionality.",
    required: true,
    enabled: true
  },
  {
    category: "analytics",
    title: "Analytics Cookies",
    description:
      "Help Nexivo understand traffic, booking funnel performance, destination demand, and product usage.",
    required: false,
    enabled: false
  },
  {
    category: "marketing",
    title: "Marketing Cookies",
    description:
      "Support promotions, sponsored placements, remarketing, campaign measurement, and personalized offers.",
    required: false,
    enabled: false
  },
  {
    category: "personalization",
    title: "Personalization Cookies",
    description:
      "Remember preferences such as language, currency, recent searches, favorite services, and destination interests.",
    required: false,
    enabled: true
  },
  {
    category: "third-party",
    title: "Third-Party Integrations",
    description:
      "Used for payment gateways, maps, video demos, customer support widgets, and future analytics providers.",
    required: false,
    enabled: false
  }
];

export const dataRequestTypes: DataRequest[] = [
  {
    id: "dr-001",
    type: "access",
    title: "Access My Data",
    description: "Request a summary of personal data stored in Nexivo and connected DSS services.",
    status: "draft",
    createdAt: "Not submitted"
  },
  {
    id: "dr-002",
    type: "export",
    title: "Export My Data",
    description: "Request a downloadable export of bookings, profile, preferences, and account data.",
    status: "draft",
    createdAt: "Not submitted"
  },
  {
    id: "dr-003",
    type: "delete",
    title: "Delete My Account",
    description: "Request account deletion where legally and operationally permitted.",
    status: "draft",
    createdAt: "Not submitted"
  },
  {
    id: "dr-004",
    type: "rectify",
    title: "Correct My Data",
    description: "Request correction of inaccurate customer or business account information.",
    status: "draft",
    createdAt: "Not submitted"
  },
  {
    id: "dr-005",
    type: "withdraw-consent",
    title: "Withdraw Consent",
    description: "Withdraw optional marketing, analytics, or personalization consent.",
    status: "draft",
    createdAt: "Not submitted"
  }
];

export const securityControls: SecurityControl[] = [
  {
    id: "sec-001",
    title: "Secure Account Sessions",
    description: "Prepared for access tokens, refresh tokens, session expiry, and device/session monitoring.",
    area: "account",
    status: "ready"
  },
  {
    id: "sec-002",
    title: "Card Tokenization",
    description: "Payment card details should be handled by payment gateways, not stored directly by Nexivo.",
    area: "payments",
    status: "planned"
  },
  {
    id: "sec-003",
    title: "Role-Based Partner Access",
    description: "Partner portal staff access should be restricted by product, branch, and permission scope.",
    area: "business",
    status: "ready"
  },
  {
    id: "sec-004",
    title: "Document Vault Protection",
    description: "Passport, ID, and driving license data should use strict access controls and audit logs.",
    area: "data",
    status: "planned"
  },
  {
    id: "sec-005",
    title: "GDPR-Ready Data Requests",
    description: "Nexivo should support access, export, deletion, correction, and consent withdrawal requests.",
    area: "compliance",
    status: "ready"
  },
  {
    id: "sec-006",
    title: "Tenant Data Separation",
    description: "DSS Central Platform must separate data between hotels, car rental companies, and laundries.",
    area: "business",
    status: "ready"
  }
];

export const privacyPrinciples = [
  "Collect only necessary customer and business data",
  "Keep card details inside secure payment gateway systems",
  "Use clear consent for analytics, marketing, and personalization",
  "Support English, Arabic, and future European privacy pages",
  "Prepare GDPR data request workflows before European expansion",
  "Maintain audit trails for business, payment, and document operations"
] as const;
