import { notFound } from "next/navigation";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { StayBookingStart } from "@/features/stays/components/stay-booking-start";
import { getCentralStayProperties } from "@/lib/marketplace/central-listings";

export default async function StayBookingPage({
  params
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const property = (await getCentralStayProperties()).find((item) => item.slug === slug);

  if (!property) {
    notFound();
  }

  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="StayLux Booking"
        title="Complete your stay booking."
        description="Enter guest details, confirm booking preference, and continue to secure payment or pay-at-property guarantee."
        spacing="compact"
      />

      <StayBookingStart property={property} className="pt-8 md:pt-10" />
    </PublicPageLayout>
  );
}
