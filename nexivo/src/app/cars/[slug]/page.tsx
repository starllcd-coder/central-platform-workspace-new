import { notFound } from "next/navigation";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { VehicleHero } from "@/features/cars/components/vehicle-hero";
import { VehicleOverview } from "@/features/cars/components/vehicle-overview";
import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";
import { getCentralRentalVehicles } from "@/lib/marketplace/central-listings";
import { formatMoney } from "@/features/currency/utils/currency-utils";

export default async function VehicleDetailsPage({
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
      <VehicleHero vehicle={vehicle} />
      <VehicleOverview vehicle={vehicle} />

      <SectionShell background="muted">
        <CtaBand
          title={`Reserve ${vehicle.name} from ${formatMoney(vehicle.pricePerDay, vehicle.currency)} per day.`}
          description="Continue to the DriveSphere-powered rental flow with driver details, pickup location, card guarantee, deposit visibility, and payment options."
          primaryLabel="Book This Vehicle"
          primaryHref={`/cars/${vehicle.slug}/book`}
          secondaryLabel="Back to Cars"
          secondaryHref="/cars"
        />
      </SectionShell>
    </PublicPageLayout>
  );
}
