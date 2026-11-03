import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { StayMarketplaceGuide } from "@/features/stays/components/stay-marketplace-guide";
import { StaySearchResults } from "@/features/stays/components/stay-search-results";
import { getCentralStayProperties } from "@/lib/marketplace/central-listings";
import { createMetadata } from "@/lib/metadata";
import { pageSeo } from "@/config/seo";

export const dynamic = "force-dynamic";

export const metadata: Metadata = createMetadata({
  ...pageSeo.stays,
  path: "/stays"
});

export default async function StaysPage() {
  const properties = await getCentralStayProperties();

  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="StayLux Marketplace"
        title="Book hotels, apartments, villas, and serviced stays."
        description="Search verified accommodation across GCC destinations with room selection, payment options, card guarantee support, and future owner/admin sync."
        primaryLabel="For Property Owners"
        primaryHref="/business/staylux"
        secondaryLabel="Explore Destinations"
        secondaryHref="/destinations"
      />

      <StaySearchResults properties={properties} />
      <StayMarketplaceGuide />
    </PublicPageLayout>
  );
}
