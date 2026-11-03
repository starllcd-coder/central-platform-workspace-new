"use client";

import { useState, type FormEvent } from "react";
import { CalendarDays, Mail, Phone, UserRound } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useBookingQuote } from "@/hooks/use-booking-quote";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import type { StayProperty } from "@/features/stays/types/stays.types";
import { getRoomById, getRoomsByPropertyId } from "@/features/stays/data/stay-rooms";
import { formatMoney } from "@/features/currency/utils/currency-utils";
import { calculateStayTotal, calculateNights } from "@/features/stays/utils/stay-pricing";
import type { StayRoom } from "@/features/stays/types/stay-booking.types";

type StayBookingStartProps = {
  property: StayProperty;
  className?: string;
};

export function StayBookingStart({ property, className }: StayBookingStartProps) {
  const router = useRouter();
  const { quote, review, clearQuote } = useBookingQuote();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const searchParams = useSearchParams();
  const selectedRoomId = searchParams.get("room");
  const centralRoom: StayRoom | undefined = property.providerResourceId
    ? {
        id: property.providerResourceId,
        propertyId: property.id,
        name: property.providerResourceName || "Available unit",
        slug: property.providerResourceId,
        description: property.shortDescription,
        maxGuests: 4,
        bedType: "Provider configured",
        size: "Provider inventory",
        pricePerNight: property.pricePerNight,
        currency: property.currency,
        refundable: property.freeCancellation,
        breakfastIncluded: false,
        availableUnits: 1,
        imageUrl: property.imageUrl
      }
    : undefined;
  const fallbackRoom = getRoomsByPropertyId(property.id)[0] ?? centralRoom;
  const room = selectedRoomId ? getRoomById(selectedRoomId) ?? fallbackRoom : fallbackRoom;

  if (!room) return null;

  const nights = calculateNights(startDate, endDate);
  const total = calculateStayTotal(room.pricePerNight, nights);

  async function submitBooking(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!startDate || !endDate || endDate <= startDate) {
      setError("Choose an end date after the start date.");
      return;
    }
    setSubmitting(true);
    setError("");
    const body = Object.fromEntries(new FormData(event.currentTarget).entries());
    try {
      const reviewed = await review({ ...body, listingSlug: property.slug, providerResourceId: property.providerResourceId || room.id, roomId: room.id, nights, estimatedTotal: total });
      if (!reviewed) { setSubmitting(false); return; }
      const response = await fetch("/api/booking/stays", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reviewed)
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        setError(payload?.error?.message || payload?.detail || "Unable to create stay booking.");
        setSubmitting(false);
        return;
      }
      const result = await response.json();
      const token = result.data?.confirmationToken;
      router.push(token ? `/booking-confirmation?token=${encodeURIComponent(token)}` : "/customer/bookings");
    } catch (error) {
      setError(error instanceof Error ? error.message : "The connection was interrupted. Please try again.");
      setSubmitting(false);
    }
  }

  return (
    <section className={cn("section-padding bg-luxury-mist", className)}>
      <form onChange={clearQuote} onSubmit={submitBooking} className="nexivo-container grid gap-8 lg:grid-cols-[1fr_380px]">
        <Card variant="premium">
          <CardHeader>
            <CardTitle>Guest details</CardTitle>
            <p className="text-sm leading-6 text-slate-600">
              Save your confirmation link to check this booking without signing in.
            </p>
          </CardHeader>

          <CardContent className="space-y-5">
            <div className="grid gap-5 md:grid-cols-2">
              <FormField label="Full name">
                <Input name="fullName" required placeholder="Customer full name" leftIcon={<UserRound size={17} />} />
              </FormField>

              <FormField label="Email">
                <Input name="email" required type="email" placeholder="customer@example.com" leftIcon={<Mail size={17} />} />
              </FormField>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <FormField label="Phone number">
                <Input name="phone" required placeholder="+968..." leftIcon={<Phone size={17} />} />
              </FormField>

              <FormField label="Guests">
                <Input name="guests" required type="number" min={1} max={room.maxGuests} defaultValue={2} />
              </FormField>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <FormField label="Check-in">
                <Input name="checkIn" value={startDate} onChange={(event) => setStartDate(event.target.value)} required type="date" leftIcon={<CalendarDays size={17} />} />
              </FormField>

              <FormField label="Check-out">
                <Input name="checkOut" value={endDate} min={startDate || undefined} onChange={(event) => setEndDate(event.target.value)} required type="date" leftIcon={<CalendarDays size={17} />} />
              </FormField>
            </div>

            <FormField
              label="Payment option"
              description="Card guarantee can be required for pay-at-property depending on the property policy."
            >
              <Select name="paymentMethod" defaultValue="pay-at-property">
                <option value="pay-online">Pay online</option>
                {property.payAtProperty ? <option value="pay-at-property">Pay at property</option> : null}
              </Select>
            </FormField>

            <p className="text-sm text-slate-600">{process.env.NODE_ENV !== "production" ? "Test checkout: no money will be collected." : "Online payments are processed through the configured payment gateway."}</p>

            {quote ? <p role="status" className="text-sm text-slate-600">Current quote: {quote.amount} {quote.currency}. Confirm to submit your booking.</p> : null}
            {error ? <p className="text-sm text-red-600">{error}</p> : null}
            <Button type="submit" disabled={submitting} variant="luxury" size="lg" fullWidth>
              {submitting ? "Submitting..." : quote ? "Confirm booking" : "Review price"}
            </Button>
          </CardContent>
        </Card>

        <aside className="h-fit rounded-4xl border border-slate-200 bg-white p-6 shadow-premium">
          <img
            src={property.imageUrl}
            alt={property.name}
            className="h-44 w-full rounded-3xl object-cover"
          />

          <h2 className="mt-5 font-heading text-2xl font-semibold text-luxury-ink">
            {property.name}
          </h2>

          <p className="mt-2 text-sm text-slate-600">
            {property.area}, {property.city}
          </p>

          <div className="mt-5 rounded-3xl bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-500">Selected room</p>
            <p className="mt-1 font-heading text-lg font-semibold text-luxury-ink">
              {room.name}
            </p>
            <p className="mt-2 text-sm text-slate-600">{room.bedType} • {room.size}</p>
          </div>

          <div className="mt-5 space-y-3 text-sm text-slate-600">
            <div className="flex justify-between">
              <span>{formatMoney(room.pricePerNight, room.currency)} × {nights} night</span>
              <span>{formatMoney(quote ? Number(quote.amount) : total, room.currency)}</span>
            </div>
            <div className="flex justify-between">
              <span>Taxes & fees</span>
              <span>Calculated later</span>
            </div>
          </div>

          <div className="mt-5 border-t border-slate-200 pt-5">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-700">Estimated total</span>
              <span className="font-heading text-2xl font-semibold text-luxury-ink">
                {formatMoney(quote ? Number(quote.amount) : total, room.currency)}
              </span>
            </div>
          </div>
        </aside>
      </form>
    </section>
  );
}
