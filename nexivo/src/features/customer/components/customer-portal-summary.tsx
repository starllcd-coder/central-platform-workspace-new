import { CalendarCheck2, Heart, ShieldCheck, Star } from "lucide-react";
import { DashboardStatCard } from "@/features/dashboard/components/dashboard-stat-card";

export function CustomerPortalSummary({ upcoming = 0 }: { upcoming?: number }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
      <DashboardStatCard label="Upcoming" value={String(upcoming)} description="Active stays, cars, and laundry orders." />
      <DashboardStatCard label="Favorites" value="0" description="Saved stays, cars, and providers." />
      <DashboardStatCard label="Reward Points" value="0" description="Available Nexivo loyalty balance." />
      <DashboardStatCard label="Verified Docs" value="0" description="Ready for travel and rental flows." />
    </div>
  );
}

export const customerQuickActions = [
  { label: "Search Stays", href: "/stays", icon: CalendarCheck2 },
  { label: "Rent a Car", href: "/cars", icon: Star },
  { label: "Order Laundry", href: "/laundry", icon: Heart },
  { label: "Manage Documents", href: "/customer/documents", icon: ShieldCheck }
] as const;
