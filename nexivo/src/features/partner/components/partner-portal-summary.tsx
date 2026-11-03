import { Building2, CalendarCheck2, FileText, WalletCards } from "lucide-react";
import { DashboardStatCard } from "@/features/dashboard/components/dashboard-stat-card";

export function PartnerPortalSummary({ activeListings = 0, bookings = 0, revenue = "0" }: { activeListings?: number; bookings?: number; revenue?: string }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
      <DashboardStatCard label="Active Listings" value={String(activeListings)} description="StayLux, DriveSphere, and Laundrex listings." />
      <DashboardStatCard label="Partner Bookings" value={String(bookings)} description="Marketplace bookings and service orders." />
      <DashboardStatCard label="Revenue" value={revenue} description="Estimated gross marketplace value." />
      <DashboardStatCard label="Open Support" value="Not connected" description="Business support tickets requiring attention." />
    </div>
  );
}

export const partnerQuickActions = [
  { label: "Manage Listings", href: "/partner/listings", icon: Building2 },
  { label: "View Bookings", href: "/partner/bookings", icon: CalendarCheck2 },
  { label: "Billing", href: "/partner/billing", icon: WalletCards },
  { label: "Reports", href: "/partner/reports", icon: FileText }
] as const;
