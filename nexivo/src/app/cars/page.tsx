import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { CarMarketplaceGuide } from "@/features/cars/components/car-marketplace-guide";
import { CarSearchResults } from "@/features/cars/components/car-search-results";
import { getCentralRentalVehicles } from "@/lib/marketplace/central-listings";
import { createMetadata } from "@/lib/metadata";
import { pageSeo } from "@/config/seo";

export const dynamic = "force-dynamic";

export const metadata: Metadata = createMetadata({
  ...pageSeo.cars,
  path: "/cars"
});

export default async function CarsPage() {
  const vehicles = await getCentralRentalVehicles();

  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="DriveSphere Marketplace"
        title="Rent cars across GCC cities with confidence."
        description="Search economy cars, SUVs, luxury vehicles, vans, airport pickups, verified fleet partners, and clear rental policies."
        primaryLabel="Add Your Fleet"
        primaryHref="/business/drivesphere"
        secondaryLabel="Business Pricing"
        secondaryHref="/pricing"
      />

      <CarSearchResults vehicles={vehicles} />
      <CarMarketplaceGuide />
    </PublicPageLayout>
  );
}
