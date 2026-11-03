import { PartnerListingsTable } from "@/features/partner/components/partner-listings-table";
import { getPartnerDashboard } from "@/lib/integrations/live-dashboards";
import { DashboardDataUnavailable } from "@/features/dashboard/components/dashboard-data-unavailable";

export default async function PartnerListingsPage() {
  const data = await getPartnerDashboard();
  if (!data) return <DashboardDataUnavailable />;
  const { bookings: partnerBookings, invoices: partnerInvoices, listings: partnerListings, metrics: partnerReportMetrics, staff: partnerStaff } = data;
  return <PartnerListingsTable listings={partnerListings} />;
}
