import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";
import { PricingCardsGrid } from "@/features/pricing/components/pricing-cards-grid";
import { PricingFaqSection } from "@/features/pricing/components/pricing-faq-section";
import { createMetadata } from "@/lib/metadata";
import { pageSeo } from "@/config/seo";

export const metadata: Metadata = createMetadata({
  ...pageSeo.pricing,
  path: "/pricing"
});

export default function PricingPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Business Pricing"
        title="Flexible setup, commission, and subscription models."
        description="Show clear starting prices publicly, but keep final commissions and custom commercial terms adjustable through DSS Central Platform."
        primaryLabel="Request Custom Proposal"
        primaryHref="/business/request-demo"
        spacing="compact"
      />

      <PricingCardsGrid className="pt-4 md:pt-6" />
      <PricingFaqSection />

      <SectionShell background="default">
        <CtaBand
          title="Need a custom proposal for your business?"
          description="Pricing depends on product modules, business size, country, marketplace participation, integrations, and long-term commercial structure."
          primaryLabel="Request Demo"
          primaryHref="/business/request-demo"
          secondaryLabel="View Business Solutions"
          secondaryHref="/business/solutions"
        />
      </SectionShell>
    </PublicPageLayout>
  );
}
