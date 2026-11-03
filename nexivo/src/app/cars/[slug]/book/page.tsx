import { notFound } from "next/navigation";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { CarBookingStart } from "@/features/cars/components/car-booking-start";
import { getCentralRentalVehicles } from "@/lib/marketplace/central-listings";

export default async function CarBookingPage({
  params
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const vehicle = (await getCentralRentalVehicles()).find((item) => item.slug === slug);

  if (!vehicle) {
    notFound();
  }

  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="DriveSphere Booking"
        title="Complete your car rental booking."
        description="Enter driver details, confirm pickup and return locations, choose payment option, and continue to secure reservation."
        spacing="compact"
      />

      <CarBookingStart vehicle={vehicle} className="pt-8 md:pt-10" />
    </PublicPageLayout>
  );
}
