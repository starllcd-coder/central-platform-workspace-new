import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { DestinationGrid } from "@/features/destinations/components/destination-grid";
import { createMetadata } from "@/lib/metadata";
import { pageSeo } from "@/config/seo";

export const metadata: Metadata = createMetadata({
  ...pageSeo.destinations,
  path: "/destinations"
});

export default function DestinationsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="GCC Destination Guides"
        title="Explore GCC cities with stays, cars, and laundry services."
        description="Destination pages help customers discover where to stay, how to move around, and what services they can use after arrival."
        primaryLabel="Search Stays"
        primaryHref="/stays"
        secondaryLabel="Search Cars"
        secondaryHref="/cars"
      />

      <DestinationGrid />
    </PublicPageLayout>
  );
}
