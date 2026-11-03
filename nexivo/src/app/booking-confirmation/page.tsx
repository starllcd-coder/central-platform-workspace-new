import Link from "next/link";
import { CheckoutActions } from "@/features/customer/components/checkout-actions";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorState } from "@/components/feedback/error-state";
import { centralPlatformRequest } from "@/lib/integrations/central-platform-api";

export const metadata = { title: "Booking confirmation | Nexivo", robots: { index: false, follow: false } };
type Confirmation = {
  bookingId: string; tenantName: string; moduleName: string; status: string;
  paymentMethod: string; fulfillmentStatus: string; paymentStatus: string; amount: string; currency: string;
};

export default async function BookingConfirmationPage({ searchParams }: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;
  let booking: Confirmation;
  try {
    if (!token || typeof token !== "string") throw new Error("Missing confirmation link");
    booking = await centralPlatformRequest<Confirmation>(`/bookings/confirmation/?token=${encodeURIComponent(token)}`);
  } catch {
    return <ErrorState title="Confirmation unavailable" description="This link may have expired, or the booking service is temporarily unavailable. Please try again or sign in to view your bookings." showBack={false} />;
  }
  return (
    <PublicPageLayout>
      <PageHero eyebrow={booking.moduleName} title="Your booking request." description="Save this confirmation link to check the latest provider status. The link is valid for 24 hours." />
      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container max-w-3xl">
          <Card variant="premium">
            <CardHeader><CardTitle>{booking.tenantName}</CardTitle></CardHeader>
            <CardContent className="space-y-4 text-sm text-slate-600">
              <p>Reference: <strong>{booking.bookingId}</strong></p>
              <p>Status: {booking.status.replace(/_/g, " ")}</p>
              <p>Provider: {booking.fulfillmentStatus.replace(/_/g, " ")}</p>
              <p>Total: {booking.amount} {booking.currency}</p>
              <p>Payment: {booking.paymentStatus === "test_unpaid" ? "Test checkout ? no money collected" : booking.paymentStatus.replace(/_/g, " ")}</p>
              <CheckoutActions token={token || ""} fulfillment={booking.fulfillmentStatus} payment={booking.paymentStatus} method={booking.paymentMethod} />
              <Link href="/customer/bookings" className="font-semibold text-brand-700 hover:underline">View account bookings</Link>
            </CardContent>
          </Card>
        </div>
      </section>
    </PublicPageLayout>
  );
}
