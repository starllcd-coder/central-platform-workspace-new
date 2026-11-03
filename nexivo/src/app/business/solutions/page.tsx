import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { BusinessMarketingHero } from "@/features/business/components/business-marketing-hero";
import { DssProductsSection } from "@/features/business/components/dss-products-section";
import { BusinessTrustSection } from "@/features/business/components/business-trust-section";

export default function BusinessSolutionsPage() {
  return (
    <PublicPageLayout>
      <BusinessMarketingHero
        eyebrow="DSS Solutions"
        title="Explore the software products powering Nexivo."
        description="StayLux, DriveSphere, Laundrex, and DSS Central Platform work together to create a unified customer marketplace and business operations ecosystem."
        primaryLabel="Request Demo"
        primaryHref="/business/request-demo"
        secondaryLabel="Pricing"
        secondaryHref="/pricing"
      />

      <DssProductsSection />
      <BusinessTrustSection />
    </PublicPageLayout>
  );
}
