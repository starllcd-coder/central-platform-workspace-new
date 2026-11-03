import { ConnectedAppLauncher } from "@/features/partner/components/connected-app-launcher";
import { PartnerBillingPanel } from "@/features/partner/components/partner-billing-panel";
import { PartnerBookingsTable } from "@/features/partner/components/partner-bookings-table";
import { PartnerListingsTable } from "@/features/partner/components/partner-listings-table";
import { PartnerPortalSummary } from "@/features/partner/components/partner-portal-summary";
import { PartnerQuickActions } from "@/features/partner/components/partner-quick-actions";
import { PartnerReportsGrid } from "@/features/partner/components/partner-reports-grid";
import { getPartnerDashboard } from "@/lib/integrations/live-dashboards";
import { DashboardDataUnavailable } from "@/features/dashboard/components/dashboard-data-unavailable";

export default async function PartnerDashboardPage() {
  const data = await getPartnerDashboard();
  if (!data) return <DashboardDataUnavailable />;
  const { bookings: partnerBookings, invoices: partnerInvoices, listings: partnerListings, metrics: partnerReportMetrics, staff: partnerStaff } = data;
  return (
    <div className="space-y-6">
      <PartnerPortalSummary activeListings={data.activeListings} bookings={data.bookingCount} revenue={data.gross} />
      <PartnerQuickActions />
      <ConnectedAppLauncher apps={data.launches} />
      <PartnerReportsGrid metrics={partnerReportMetrics} />
      <PartnerListingsTable listings={partnerListings} />
      <PartnerBookingsTable bookings={partnerBookings} />
      <PartnerBillingPanel invoices={partnerInvoices.slice(0, 2)} />
    </div>
  );
}