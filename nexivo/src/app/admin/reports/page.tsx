import { AdminReportsGrid } from "@/features/admin/components/admin-reports-grid";
import { getAdminDashboard } from "@/lib/integrations/live-dashboards";
import { DashboardDataUnavailable } from "@/features/dashboard/components/dashboard-data-unavailable";

export default async function AdminReportsPage() {
  const data = await getAdminDashboard();
  if (!data) return <DashboardDataUnavailable />;
  const { metrics: adminMetrics, products: productAnalytics, monitoring: monitoringServices, auditLogs, reports: adminReports } = data;
  return <AdminReportsGrid reports={adminReports} />;
}
