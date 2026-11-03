import { CalendarCheck2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PartnerBooking } from "@/features/partner/types/partner.types";
import {
  getPartnerProductBadgeVariant,
  getPartnerProductLabel
} from "@/features/partner/components/partner-utils";

type PartnerBookingsTableProps = {
  bookings: PartnerBooking[];
};

export function PartnerBookingsTable({ bookings }: PartnerBookingsTableProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Partner Bookings</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Marketplace bookings and orders generated through Nexivo.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {bookings.map((booking) => (
          <div
            key={booking.id}
            className="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft md:flex-row md:items-center md:justify-between"
          >
            <div className="flex gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <CalendarCheck2 size={21} />
              </div>

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                    {booking.service}
                  </h3>
                  <Badge variant={getPartnerProductBadgeVariant(booking.product)}>
                    {getPartnerProductLabel(booking.product)}
                  </Badge>
                </div>
                <p className="mt-1 text-sm text-slate-600">
                  {booking.customer} • {booking.date}
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
        ))}
      </CardContent>
    </Card>
  );
}
