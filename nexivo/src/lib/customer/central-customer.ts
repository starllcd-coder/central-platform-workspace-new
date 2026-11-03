import { cookies } from "next/headers";
import type { CustomerBooking, CustomerBookingStatus, CustomerBookingType } from "@/features/customer/types/customer.types";
import { NEXIVO_SESSION_COOKIE, verifySessionToken } from "@/lib/auth/session";
import { centralPlatformRequest, type CentralListResponse } from "@/lib/integrations/central-platform-api";

type CentralCustomerBooking = {
  bookingId: string;
  tenantName: string;
  moduleCode: string;
  moduleName: string;
  status: string;
  fulfillmentStatus: string;
  amount: string;
  currency: string;
  createdAt: string;
};

function bookingType(moduleCode: string): CustomerBookingType {
  if (moduleCode === "drivesphere") return "car";
  if (moduleCode === "laundrex") return "laundry";
  return "stay";
}

function bookingStatus(value: string): CustomerBookingStatus {
  if (value === "confirmed" || value === "completed" || value === "cancelled") return value;
  return "pending";
}

export async function getCustomerBookings(): Promise<CustomerBooking[]> {
  const cookieStore = await cookies();
  const session = await verifySessionToken(cookieStore.get(NEXIVO_SESSION_COOKIE)?.value);
  if (!session || session.role !== "customer") return [];

  try {
    const response = await centralPlatformRequest<CentralListResponse<CentralCustomerBooking>>(
      "/customer/bookings/",
      { headers: { Authorization: `Bearer ${session.accessToken}` } }
    );
    return response.results.map((booking) => ({
      id: booking.bookingId,
      type: bookingType(booking.moduleCode),
      title: booking.tenantName,
      provider: booking.moduleName,
      location: booking.fulfillmentStatus.replace(/_/g, " "),
      dateLabel: new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(booking.createdAt)),
      amount: `${booking.amount} ${booking.currency}`,
      status: bookingStatus(booking.status)
    }));
  } catch {
    throw new Error("Customer bookings could not be loaded. Please try again.");
  }
}
