import { AdminMetricsGrid } from "@/features/admin/components/admin-metrics-grid";
import { AdminOperationsSummary } from "@/features/admin/components/admin-operations-summary";
import { AdminQuickActions } from "@/features/admin/components/admin-quick-actions";
import { MonitoringServicesGrid } from "@/features/admin/components/monitoring-services-grid";
import { ProductAnalyticsTable } from "@/features/admin/components/product-analytics-table";
import { getAdminDashboard } from "@/lib/integrations/live-dashboards";
import { DashboardDataUnavailable } from "@/features/dashboard/components/dashboard-data-unavailable";

export default async function AdminPage() {
  const data = await getAdminDashboard();
  if (!data) return <DashboardDataUnavailable />;
  const { metrics: adminMetrics, products: productAnalytics, monitoring: monitoringServices, auditLogs, reports: adminReports } = data;
  return (
    <div className="space-y-6">
      <AdminOperationsSummary systemStatus={data.systemStatus} auditCount={data.auditCount} reportCount={data.reports.length} />
      <AdminQuickActions />
      <AdminMetricsGrid metrics={adminMetrics} />
      <ProductAnalyticsTable products={productAnalytics} />
      <MonitoringServicesGrid services={monitoringServices.slice(0, 4)} />
    </div>
  );
}