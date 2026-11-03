import type {
  AdminMetric,
  AdminReport,
  AuditLogEntry,
  MonitoringService,
  ProductAnalytics
} from "@/features/admin/types/admin.types";

export const adminMetrics: AdminMetric[] = [
  { label: "Marketplace Bookings", value: "0", description: "Confirmed marketplace bookings and orders.", trend: "stable" },
  { label: "Gross Booking Value", value: "0 OMR", description: "Marketplace gross booking value.", trend: "stable" },
  { label: "Business Leads", value: "0", description: "Business onboarding leads.", trend: "stable" },
  { label: "Active Partners", value: "0", description: "Verified marketplace partners.", trend: "stable" }
];

export const productAnalytics: ProductAnalytics[] = [];
export const monitoringServices: MonitoringService[] = [];
export const auditLogs: AuditLogEntry[] = [];
export const adminReports: AdminReport[] = [];
