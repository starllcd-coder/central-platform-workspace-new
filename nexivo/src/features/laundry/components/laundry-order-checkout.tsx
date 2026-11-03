"use client";

import { useState, type FormEvent } from "react";
import { CalendarDays, CreditCard, Mail, MapPin, Phone, UserRound } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useBookingQuote } from "@/hooks/use-booking-quote";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { LaundryProvider } from "@/features/laundry/types/laundry.types";
import {
  getLaundryServiceById,
  getLaundryServicesByProvider
} from "@/features/laundry/data/laundry-services";
import { formatMoney } from "@/features/currency/utils/currency-utils";
import { calculateLaundryOrderTotal } from "@/features/laundry/utils/laundry-pricing";

type LaundryOrderCheckoutProps = {
  provider: LaundryProvider;
};

export function LaundryOrderCheckout({ provider }: LaundryOrderCheckoutProps) {
  const router = useRouter();
  const { quote, review, clearQuote } = useBookingQuote();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const searchParams = useSearchParams();
  const selectedServiceId = searchParams.get("service");
  const fallbackService = getLaundryServicesByProvider(provider.id)[0];
  const centralService = provider.providerResourceId
    ? {
        id: provider.providerResourceId,
        providerId: provider.id,
        name: provider.providerResourceName || "Laundry service",
        serviceType: "wash-fold" as const,
        description: provider.shortDescription,
        price: provider.minimumOrder,
        unit: provider.providerResourceUnit || "order" as const,
        currency: provider.currency,
        estimatedTime: "Provider schedule"
      }
    : undefined;
  const service = selectedServiceId
    ? getLaundryServiceById(selectedServiceId) ?? fallbackService ?? centralService
    : fallbackService ?? centralService;

  if (!service) return null;

  const quantity = 1;
  const subtotal = calculateLaundryOrderTotal([
    {
      price: service.price,
      quantity
    }
  ]);

  async function submitOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    const body = Object.fromEntries(new FormData(event.currentTarget).entries());
    try {
      const reviewed = await review({ ...body, listingSlug: provider.slug, providerResourceId: provider.providerResourceId || service.id, serviceId: service.id, serviceName: service.name, itemName: service.name, estimatedTotal: subtotal });
      if (!reviewed) { setSubmitting(false); return; }
      const response = await fetch("/api/booking/laundry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reviewed)
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        setError(payload?.error?.message || payload?.detail || "Unable to create laundry order.");
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
    <section className="section-padding bg-luxury-mist">
      <form onChange={clearQuote} onSubmit={submitOrder} className="nexivo-container grid gap-8 lg:grid-cols-[1fr_380px]">
        <Card variant="premium">
          <CardHeader>
            <CardTitle>Pickup and customer details</CardTitle>
            <p className="text-sm leading-6 text-slate-600">
              A Nexivo account can be created automatically using the provided email during order
              checkout. Laundrex will manage provider operations and order tracking.
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

              <FormField label="Pickup date">
                <Input name="pickupDate" required type="date" leftIcon={<CalendarDays size={17} />} />
              </FormField>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <FormField label="Pickup time">
                <Select name="pickupSlot" defaultValue="morning">
                  <option value="morning">Morning</option>
                  <option value="afternoon">Afternoon</option>
                  <option value="evening">Evening</option>
                </Select>
              </FormField>

              <FormField label="Quantity">
                <Input name="quantity" required type="number" min={1} defaultValue={quantity} />
              </FormField>
            </div>

            <FormField label="Pickup address">
              <Input name="pickupAddress" required placeholder="Hotel, apartment, building, area..." leftIcon={<MapPin size={17} />} />
            </FormField>

            <FormField label="Delivery address">
              <Input name="deliveryAddress" placeholder="Same as pickup or different delivery address" leftIcon={<MapPin size={17} />} />
            </FormField>

            <FormField
              label="Payment option"
              description="Laundrex is designed for subscription-based businesses, not per-order commission."
            >
              <Select name="paymentMethod" defaultValue="pay-on-delivery">
                <option value="pay-online">Pay online</option>
                <option value="pay-on-delivery">Pay on delivery</option>
              </Select>
            </FormField>

            <FormField label="Payment details">
              <Input placeholder="Secure payment placeholder" leftIcon={<CreditCard size={17} />} />
            </FormField>

            {quote ? <p role="status" className="text-sm text-slate-600">Current quote: {quote.amount} {quote.currency}. Confirm to submit your booking.</p> : null}
            {error ? <p className="text-sm text-red-600">{error}</p> : null}
            <Button type="submit" disabled={submitting} variant="luxury" size="lg" fullWidth>
              {submitting ? "Submitting..." : quote ? "Confirm order" : "Review price"}
            </Button>
          </CardContent>
        </Card>

        <aside className="h-fit rounded-4xl border border-slate-200 bg-white p-6 shadow-premium">
          <img
            src={provider.imageUrl}
            alt={provider.name}
            className="h-44 w-full rounded-3xl object-cover"
          />

          <h2 className="mt-5 font-heading text-2xl font-semibold text-luxury-ink">
            {provider.name}
          </h2>

          <p className="mt-2 text-sm text-slate-600">
            {provider.area}, {provider.city}
          </p>

          <div className="mt-5 rounded-3xl bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-500">Selected service</p>
            <p className="mt-1 font-heading text-lg font-semibold text-luxury-ink">
              {service.name}
            </p>
            <p className="mt-2 text-sm text-slate-600">
              {service.estimatedTime} • charged per {service.unit}
            </p>
          </div>

          <div className="mt-5 space-y-3 text-sm text-slate-600">
            <div className="flex justify-between">
              <span>
                {formatMoney(service.price, service.currency)} × {quantity}
              </span>
              <span>{formatMoney(quote ? Number(quote.amount) : subtotal, service.currency)}</span>
            </div>
            <div className="flex justify-between">
              <span>Pickup / delivery</span>
              <span>Provider policy</span>
            </div>
            <div className="flex justify-between">
              <span>Minimum order</span>
              <span>{formatMoney(provider.minimumOrder, provider.currency)}</span>
            </div>
          </div>

          <div className="mt-5 border-t border-slate-200 pt-5">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-700">Estimated subtotal</span>
              <span className="font-heading text-2xl font-semibold text-luxury-ink">
                {formatMoney(quote ? Number(quote.amount) : subtotal, service.currency)}
              </span>
            </div>
          </div>
        </aside>
      </form>
    </section>
  );
}
