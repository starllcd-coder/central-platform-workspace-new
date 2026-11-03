import { CustomerBookingsList } from "@/features/customer/components/customer-bookings-list";
import { getCustomerBookings } from "@/lib/customer/central-customer";

export default async function CustomerBookingsPage() {
  const customerBookings = await getCustomerBookings();
  return <CustomerBookingsList bookings={customerBookings} />;
}
