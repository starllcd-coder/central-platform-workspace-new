export type AdminMetric = {
  label: string;
  value: string;
  description: string;
  trend: "up" | "down" | "stable";
};

export type ProductAnalytics = {
  product: "StayLux" | "DriveSphere" | "Laundrex";
  bookings: number;
  revenue: string;
  activeListings: number;
  conversionRate: string;
};

export type MonitoringStatus = "healthy" | "warning" | "critical" | "maintenance";

export type MonitoringService = {
  id: string;
  name: string;
  area: "marketplace" | "payments" | "booking" | "central-platform" | "notifications" | "database";
  status: MonitoringStatus;
  uptime: string;
  latency: string;
  lastChecked: string;
};

export type AuditLogAction =
  | "login"
  | "booking-created"
  | "payment-updated"
  | "listing-updated"
  | "pricing-changed"
  | "consent-updated"
  | "data-request-created"
  | "integration-sync";

export type AuditLogEntry = {
  id: string;
  action: AuditLogAction;
  actor: string;
  actorRole: "customer" | "partner" | "admin" | "system";
  target: string;
  description: string;
  ipAddress: string;
  createdAt: string;
};

export type AdminReport = {
  id: string;
  title: string;
  category: "marketplace" | "finance" | "partner" | "customer" | "compliance";
  description: string;
  frequency: "daily" | "weekly" | "monthly" | "quarterly";
  status: "ready" | "draft" | "planned";
};
