"use client";

import { useAuthSession } from "@/features/auth/utils/use-auth-session";
import { DashboardShell } from "@/features/dashboard/components/dashboard-shell";
import { customerDashboardNavigation } from "@/features/dashboard/data/dashboard-navigation";

const allowedRoles = ["customer"] as const;

export default function CustomerLayout({
  children
}: {
  children: React.ReactNode;
}) {
  useAuthSession(allowedRoles);

  return (
    <DashboardShell
      title="Customer Dashboard"
      description="Manage your Nexivo bookings, rewards, favorites, documents, reviews, notifications, and preferences from one account."
      navigation={customerDashboardNavigation}
      roleLabel="Customer Portal"
    >
      {children}
    </DashboardShell>
  );
}
