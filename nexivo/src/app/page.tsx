import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";
import { BusinessIntroSection } from "@/features/home/components/business-intro-section";
import { FeaturedDestinationsSection } from "@/features/home/components/featured-destinations-section";
import { HomeHero } from "@/features/home/components/home-hero";
import { MarketplacePreviewSection } from "@/features/home/components/marketplace-preview-section";
import { MarketplaceServiceBenefits } from "@/features/marketplace/components/marketplace-service-benefits";
import { createMetadata } from "@/lib/metadata";
import { pageSeo } from "@/config/seo";

export const metadata: Metadata = createMetadata({
  ...pageSeo.home,
  path: "/"
});

export default function HomePage() {
  return (
    <PublicPageLayout>
      <HomeHero />
      <MarketplaceServiceBenefits />
      <FeaturedDestinationsSection />
      <MarketplacePreviewSection />
      <BusinessIntroSection />

      <SectionShell background="muted">
        <CtaBand
          title="Start with one journey: stay, car, and laundry."
          description="Nexivo connects GCC customer demand with DSS-powered business software for hotels, car rentals, and laundry providers."
          primaryLabel="Explore Stays"
          primaryHref="/stays"
          secondaryLabel="For Business"
          secondaryHref="/business"
        />
      </SectionShell>
    </PublicPageLayout>
  );
}
