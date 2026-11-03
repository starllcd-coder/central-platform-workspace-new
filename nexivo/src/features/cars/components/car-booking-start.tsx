"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { CalendarDays, Mail, Phone, UserRound } from "lucide-react";
import { useBookingQuote } from "@/hooks/use-booking-quote";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import type { RentalVehicle } from "@/features/cars/types/cars.types";
import { getVehiclePolicy } from "@/features/cars/data/vehicle-policies";
import { formatMoney } from "@/features/currency/utils/currency-utils";
import { calculateCarRentalTotal, calculateRentalDays } from "@/features/cars/utils/car-pricing";

type CarBookingStartProps = {
  vehicle: RentalVehicle;
  className?: string;
};

export function CarBookingStart({ vehicle, className }: CarBookingStartProps) {
  const router = useRouter();
  const { quote, review, clearQuote } = useBookingQuote();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const policy = getVehiclePolicy(vehicle.id);
  const rentalDays = calculateRentalDays(startDate, endDate);
  const total = calculateCarRentalTotal(vehicle.pricePerDay, rentalDays);

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
      const reviewed = await review({ ...body, listingSlug: vehicle.slug, providerResourceId: vehicle.providerResourceId || vehicle.id, rentalDays, estimatedTotal: total });
      if (!reviewed) { setSubmitting(false); return; }
      const response = await fetch("/api/booking/cars", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reviewed)
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        setError(payload?.error?.message || payload?.detail || "Unable to create rental booking.");
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
            <CardTitle>Driver details</CardTitle>
            <p className="text-sm leading-6 text-slate-600">
              Save your confirmation link to check this booking without signing in.
              Driver documents can later be saved in the secure Travel Document Vault.
            </p>
          </CardHeader>

          <CardContent className="space-y-5">
            <div className="grid gap-5 md:grid-cols-2">
              <FormField label="Driver full name">
                <Input name="fullName" required placeholder="Driver full name" leftIcon={<UserRound size={17} />} />
              </FormField>

              <FormField label="Email">
                <Input name="email" required type="email" placeholder="driver@example.com" leftIcon={<Mail size={17} />} />
              </FormField>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <FormField label="Phone number">
                <Input name="phone" required placeholder="+968..." leftIcon={<Phone size={17} />} />
              </FormField>

              <FormField label="Driving license number">
                <Input name="driverLicenseNumber" required placeholder="License number" />
              </FormField>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <FormField label="Pickup date">
                <Input name="pickupDate" value={startDate} onChange={(event) => setStartDate(event.target.value)} required type="date" leftIcon={<CalendarDays size={17} />} />
              </FormField>

              <FormField label="Return date">
                <Input name="returnDate" value={endDate} min={startDate || undefined} onChange={(event) => setEndDate(event.target.value)} required type="date" leftIcon={<CalendarDays size={17} />} />
              </FormField>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <FormField label="Pickup location">
                <Input name="pickupLocation" required defaultValue={vehicle.pickupLocation} />
              </FormField>

              <FormField label="Return location">
                <Input name="returnLocation" required defaultValue={vehicle.pickupLocation} />
              </FormField>
            </div>

            <FormField
              label="Payment option"
              description="Card guarantee may be required for pay-at-pickup bookings depending on provider policy."
            >
              <Select name="paymentMethod" defaultValue="pay-at-pickup">
                <option value="pay-online">Pay online</option>
                {vehicle.payAtPickup ? <option value="pay-at-pickup">Pay at pickup</option> : null}
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
            src={vehicle.imageUrl}
            alt={vehicle.name}
            className="h-44 w-full rounded-3xl object-cover"
          />

          <h2 className="mt-5 font-heading text-2xl font-semibold text-luxury-ink">
            {vehicle.name}
          </h2>

          <p className="mt-2 text-sm font-semibold text-brand-700">{vehicle.companyName}</p>
          <p className="mt-1 text-sm text-slate-600">{vehicle.pickupLocation}</p>

          <div className="mt-5 rounded-3xl bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-500">Rental policy</p>
            <p className="mt-1 text-sm leading-6 text-slate-600">
              Minimum age {policy?.minimumAge ?? 21}. Deposit{" "}
              {policy?.depositRequired ? "required" : "not required"}.
            </p>
          </div>

          <div className="mt-5 space-y-3 text-sm text-slate-600">
            <div className="flex justify-between">
              <span>{formatMoney(vehicle.pricePerDay, vehicle.currency)} × {rentalDays} day</span>
              <span>{formatMoney(quote ? Number(quote.amount) : total, vehicle.currency)}</span>
            </div>
            <div className="flex justify-between">
              <span>Deposit</span>
              <span>{formatMoney(vehicle.depositAmount, vehicle.currency)}</span>
            </div>
            <div className="flex justify-between">
              <span>Taxes & fees</span>
              <span>Calculated later</span>
            </div>
          </div>

          <div className="mt-5 border-t border-slate-200 pt-5">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-700">Estimated rental</span>
              <span className="font-heading text-2xl font-semibold text-luxury-ink">
                {formatMoney(quote ? Number(quote.amount) : total, vehicle.currency)}
              </span>
            </div>
          </div>
        </aside>
      </form>
    </section>
  );
}
