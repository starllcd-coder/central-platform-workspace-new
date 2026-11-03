"use client";

import { BedDouble, CalendarDays, UsersRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { StayRoom } from "@/features/stays/types/stay-booking.types";
import { useStayBookingStore } from "@/features/stays/store/stay-booking.store";
import { formatMoney } from "@/features/currency/utils/currency-utils";
import { calculateNights } from "@/features/stays/utils/stay-pricing";

type RoomSelectionCardProps = {
  room: StayRoom;
  propertySlug: string;
};

export function RoomSelectionCard({ room, propertySlug }: RoomSelectionCardProps) {
  const { startBooking } = useStayBookingStore();

  const today = new Date();
  const tomorrow = new Date();
  tomorrow.setDate(today.getDate() + 1);

  const checkIn = today.toISOString().slice(0, 10);
  const checkOut = tomorrow.toISOString().slice(0, 10);
  const nights = calculateNights(checkIn, checkOut);

  function handleStartBooking() {
    startBooking({
      propertyId: room.propertyId,
      roomId: room.id,
      checkIn,
      checkOut,
      guests: Math.min(room.maxGuests, 2),
      nights,
      paymentMethod: "pay-at-property",
      cardGuaranteeRequired: true
    });

    window.location.href = `/stays/${propertySlug}/book?room=${room.id}`;
  }

  return (
    <article className="overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-soft">
      <div className="grid gap-0 md:grid-cols-[300px_1fr]">
        <img
          src={room.imageUrl}
          alt={room.name}
          className="h-64 w-full object-cover md:h-full"
        />

        <div className="p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h3 className="font-heading text-2xl font-semibold text-luxury-ink">
                {room.name}
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{room.description}</p>
            </div>

            <div className="text-right">
              <div className="font-heading text-2xl font-semibold text-luxury-ink">
                {formatMoney(room.pricePerNight, room.currency)}
              </div>
              <p className="text-sm text-slate-500">per night</p>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            <Badge variant="outline">
              <UsersRound className="mr-1" size={13} />
              Up to {room.maxGuests} guests
            </Badge>
            <Badge variant="outline">
              <BedDouble className="mr-1" size={13} />
              {room.bedType}
            </Badge>
            <Badge variant="outline">{room.size}</Badge>
            {room.refundable ? <Badge variant="success">Refundable</Badge> : <Badge variant="secondary">Non-refundable</Badge>}
            {room.breakfastIncluded ? <Badge variant="gold">Breakfast included</Badge> : null}
          </div>

          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-slate-200 pt-5">
            <p className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600">
              <CalendarDays size={16} />
              {room.availableUnits} units available
            </p>

            <Button variant="luxury" onClick={handleStartBooking}>
              Select Room
            </Button>
          </div>
        </div>
      </div>
    </article>
  );
}
