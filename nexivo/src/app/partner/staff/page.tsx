import { PartnerStaffTable } from "@/features/partner/components/partner-staff-table";
import { getPartnerDashboard } from "@/lib/integrations/live-dashboards";
import { DashboardDataUnavailable } from "@/features/dashboard/components/dashboard-data-unavailable";

export default async function PartnerStaffPage() {
  const data = await getPartnerDashboard();
  if (!data) return <DashboardDataUnavailable />;
  const { bookings: partnerBookings, invoices: partnerInvoices, listings: partnerListings, metrics: partnerReportMetrics, staff: partnerStaff } = data;
  return <PartnerStaffTable staff={partnerStaff} />;
}
