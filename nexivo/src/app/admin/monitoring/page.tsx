import { MonitoringServicesGrid } from "@/features/admin/components/monitoring-services-grid";
import { getAdminDashboard } from "@/lib/integrations/live-dashboards";
import { DashboardDataUnavailable } from "@/features/dashboard/components/dashboard-data-unavailable";

export default async function AdminMonitoringPage() {
  const data = await getAdminDashboard();
  if (!data) return <DashboardDataUnavailable />;
  const { metrics: adminMetrics, products: productAnalytics, monitoring: monitoringServices, auditLogs, reports: adminReports } = data;
  return <MonitoringServicesGrid services={monitoringServices} />;
}
