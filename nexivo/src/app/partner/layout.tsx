"use client";

import { useAuthSession } from "@/features/auth/utils/use-auth-session";
import { DashboardShell } from "@/features/dashboard/components/dashboard-shell";
import { partnerDashboardNavigation } from "@/features/dashboard/data/dashboard-navigation";

const allowedRoles = ["partner", "admin"] as const;

export default function PartnerLayout({
  children
}: {
  children: React.ReactNode;
}) {
  useAuthSession(allowedRoles);

  return (
    <DashboardShell
      title="Partner Dashboard"
      description="Manage business listings, bookings, billing, reports, staff users, support, and DSS Central Platform-connected services."
      navigation={partnerDashboardNavigation}
      roleLabel="Partner Portal"
    >
      {children}
    </DashboardShell>
  );
}
