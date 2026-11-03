import { CustomerBookingsList } from "@/features/customer/components/customer-bookings-list";
import { CustomerFavoritesGrid } from "@/features/customer/components/customer-favorites-grid";
import { CustomerQuickActions } from "@/features/customer/components/customer-quick-actions";
import { CustomerRewardsPanel } from "@/features/customer/components/customer-rewards-panel";
import { CustomerPortalSummary } from "@/features/customer/components/customer-portal-summary";
import { customerFavorites, rewardActivities } from "@/features/customer/data/customer-dashboard-data";
import { getCustomerBookings } from "@/lib/customer/central-customer";

export default async function CustomerDashboardPage() {
  const customerBookings = await getCustomerBookings();
  return (
    <div className="space-y-6">
      <CustomerPortalSummary upcoming={customerBookings.filter((booking) => booking.status === "confirmed" || booking.status === "pending").length} />
      <CustomerQuickActions />
      <CustomerBookingsList bookings={customerBookings.slice(0, 3)} />
      <CustomerFavoritesGrid favorites={customerFavorites} />
      <CustomerRewardsPanel activities={rewardActivities.slice(0, 3)} />
    </div>
  );
}
