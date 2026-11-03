import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { LaundryMarketplaceGuide } from "@/features/laundry/components/laundry-marketplace-guide";
import { LaundrySearchResults } from "@/features/laundry/components/laundry-search-results";
import { getCentralLaundryProviders } from "@/lib/marketplace/central-listings";
import { createMetadata } from "@/lib/metadata";
import { pageSeo } from "@/config/seo";

export const dynamic = "force-dynamic";

export const metadata: Metadata = createMetadata({
  ...pageSeo.laundry,
  path: "/laundry"
});

export default async function LaundryPage() {
  const providers = await getCentralLaundryProviders();

  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Laundrex Services"
        title="Laundry pickup and delivery made simple."
        description="Search verified laundry providers, schedule pickup, select services, track orders, and manage laundry needs through Nexivo Laundrex."
        primaryLabel="Schedule Laundry"
        primaryHref="/laundry/order"
        secondaryLabel="Register Laundry Business"
        secondaryHref="/business/laundrex"
      />

      <LaundrySearchResults providers={providers} />
      <LaundryMarketplaceGuide />
    </PublicPageLayout>
  );
}
