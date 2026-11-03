import { cache } from "react";
import { cookies } from "next/headers";
import { centralPlatformRequest } from "./central-platform-api";
import { NEXIVO_SESSION_COOKIE, verifySessionToken } from "@/lib/auth/session";
import type { PartnerBooking, PartnerInvoice, PartnerListing, PartnerStaff } from "@/features/partner/types/partner.types";
import type { AdminMetric, ProductAnalytics, MonitoringService, AuditLogEntry, AdminReport } from "@/features/admin/types/admin.types";

type Metric = { label: string; value: string; description: string };
export type PartnerDashboard = { launches: { tenantCode:string;moduleCode:string;name:string }[]; bookings: PartnerBooking[]; listings: PartnerListing[]; invoices: PartnerInvoice[]; staff: PartnerStaff[];
  metrics: Metric[]; activeListings: number; bookingCount: number; gross: string };
export type AdminDashboard = { metrics: AdminMetric[]; products: ProductAnalytics[]; monitoring: MonitoringService[];
  auditLogs: AuditLogEntry[]; reports: AdminReport[]; auditCount: number; systemStatus: string };

async function load<T>(path: string, admin = false): Promise<T | null> {
  const session = await verifySessionToken((await cookies()).get(NEXIVO_SESSION_COOKIE)?.value);
  if (!session || (admin ? session.role !== "admin" : !["partner", "admin"].includes(session.role))) return null;
  try { return await centralPlatformRequest<T>(path, { headers: { Authorization: `Bearer ${session.accessToken}` }, timeoutMs: 10000 }); }
  catch { return null; }
}
export const getPartnerDashboard = cache(() => load<PartnerDashboard>("/provider/dashboard/"));
export const getAdminDashboard = cache(() => load<AdminDashboard>("/admin/dashboard/", true));
