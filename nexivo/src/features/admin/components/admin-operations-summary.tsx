import { Activity, BarChart3, FileClock, ShieldCheck } from "lucide-react";
import { DashboardStatCard } from "@/features/dashboard/components/dashboard-stat-card";

export function AdminOperationsSummary({ systemStatus = "Unavailable", auditCount = 0, reportCount = 0 }: { systemStatus?: string; auditCount?: number; reportCount?: number }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
      <DashboardStatCard label="System Status" value={systemStatus} description="Connect monitoring to display live status." />
      <DashboardStatCard label="Products" value="3" description="StayLux, DriveSphere, and Laundrex." />
      <DashboardStatCard label="Audit Events" value={String(auditCount)} description="Recorded platform audit events." />
      <DashboardStatCard label="Reports" value={String(reportCount)} description="Marketplace, finance, partner, customer, compliance." />
    </div>
  );
}

export const adminQuickActions = [
  { label: "Analytics", href: "/admin/analytics", icon: BarChart3 },
  { label: "Monitoring", href: "/admin/monitoring", icon: Activity },
  { label: "Audit Logs", href: "/admin/audit-logs", icon: FileClock },
  { label: "Reports", href: "/admin/reports", icon: ShieldCheck }
] as const;
