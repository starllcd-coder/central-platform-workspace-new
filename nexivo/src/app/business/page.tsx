import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";
import { BusinessMarketingHero } from "@/features/business/components/business-marketing-hero";
import { DssProductsSection } from "@/features/business/components/dss-products-section";
import { BusinessPricingPreview } from "@/features/business/components/business-pricing-preview";
import { BusinessTrustSection } from "@/features/business/components/business-trust-section";

export default function BusinessPage() {
  return (
    <PublicPageLayout>
      <BusinessMarketingHero
        eyebrow="For Business"
        title="Join Nexivo and grow with DSS-powered platforms."
        description="Hotels, property managers, car rental companies, and laundry businesses can join Nexivo marketplace while using DSS software to manage daily operations."
      />

      <DssProductsSection />
      <BusinessPricingPreview />
      <BusinessTrustSection />

      <SectionShell background="default">
        <CtaBand
          title="Ready to list your business on Nexivo?"
          description="Request a demo and receive a custom proposal based on your business type, size, location, and required DSS product modules."
          primaryLabel="Request Demo"
          primaryHref="/business/request-demo"
          secondaryLabel="View Pricing"
          secondaryHref="/pricing"
        />
      </SectionShell>
    </PublicPageLayout>
  );
}
