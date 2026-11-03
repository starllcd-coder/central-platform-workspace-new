import { CalendarCheck2, Car, Hotel, Shirt } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CustomerBooking } from "@/features/customer/types/customer.types";

type CustomerBookingsListProps = {
  bookings: CustomerBooking[];
};

export function CustomerBookingsList({ bookings }: CustomerBookingsListProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Bookings & Orders</CardTitle>
        <p className="text-sm text-slate-600">
          Unified view for StayLux stays, DriveSphere rentals, and Laundrex orders.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {bookings.map((booking) => {
          const Icon =
            booking.type === "stay" ? Hotel : booking.type === "car" ? Car : Shirt;

          return (
            <div
              key={booking.id}
              className="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft md:flex-row md:items-center md:justify-between"
            >
              <div className="flex gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                  <Icon size={21} />
                </div>

                <div>
                  <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                    {booking.title}
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">
                    {booking.provider} • {booking.location}
                  </p>
                  <p className="mt-1 inline-flex items-center gap-2 text-sm text-slate-500">
                    <CalendarCheck2 size={15} />
                    {booking.dateLabel}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 md:flex-col md:items-end">
                <span className="font-heading text-xl font-semibold text-luxury-ink">
                  {booking.amount}
                </span>
                <Badge
                  variant={
                    booking.status === "confirmed"
                      ? "success"
                      : booking.status === "pending"
                        ? "warning"
                        : booking.status === "completed"
                          ? "secondary"
                          : "destructive"
                  }
                >
                  {booking.status}
                </Badge>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
