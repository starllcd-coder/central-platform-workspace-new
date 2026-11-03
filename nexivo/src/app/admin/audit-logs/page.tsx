import { AuditLogsTable } from "@/features/admin/components/audit-logs-table";
import { getAdminDashboard } from "@/lib/integrations/live-dashboards";
import { DashboardDataUnavailable } from "@/features/dashboard/components/dashboard-data-unavailable";

export default async function AdminAuditLogsPage() {
  const data = await getAdminDashboard();
  if (!data) return <DashboardDataUnavailable />;
  const { metrics: adminMetrics, products: productAnalytics, monitoring: monitoringServices, auditLogs, reports: adminReports } = data;
  return <AuditLogsTable logs={auditLogs} />;
}
