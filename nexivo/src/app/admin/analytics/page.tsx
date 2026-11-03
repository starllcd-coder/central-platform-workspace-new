import { AdminMetricsGrid } from "@/features/admin/components/admin-metrics-grid";
import { ProductAnalyticsTable } from "@/features/admin/components/product-analytics-table";
import { getAdminDashboard } from "@/lib/integrations/live-dashboards";
import { DashboardDataUnavailable } from "@/features/dashboard/components/dashboard-data-unavailable";

export default async function AdminAnalyticsPage() {
  const data = await getAdminDashboard();
  if (!data) return <DashboardDataUnavailable />;
  const { metrics: adminMetrics, products: productAnalytics, monitoring: monitoringServices, auditLogs, reports: adminReports } = data;
  return (
    <div className="space-y-6">
      <AdminMetricsGrid metrics={adminMetrics} />
      <ProductAnalyticsTable products={productAnalytics} />
    </div>
  );
}
