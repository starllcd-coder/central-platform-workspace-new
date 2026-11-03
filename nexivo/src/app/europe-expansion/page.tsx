import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";

export default function EuropeExpansionPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Future Expansion"
        title="Nexivo Europe Expansion Roadmap"
        description="The Nexivo platform is architected for GCC launch first, with future support for European customers, languages, currencies, and regulations."
      />
    </PublicPageLayout>
  );
}