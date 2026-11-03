import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";
import { BusinessMarketingHero } from "@/features/business/components/business-marketing-hero";
import { ProductFeaturesSection } from "@/features/business/components/product-features-section";
import { BusinessPricingPreview } from "@/features/business/components/business-pricing-preview";
import { laundrexFeatures } from "@/features/business/data/business-marketing-data";

export default function BusinessLaundrexPage() {
  return (
    <PublicPageLayout>
      <BusinessMarketingHero
        eyebrow="Nexivo Laundrex"
        title="Laundry order management and customer service platform."
        description="Laundrex supports laundry pickup, delivery, customer orders, service catalog, branch operations, notifications, and Nexivo marketplace visibility."
        primaryLabel="Request Laundrex Demo"
        primaryHref="/business/request-demo"
      />

      <ProductFeaturesSection
        eyebrow="Laundrex Features"
        title="Laundry operations without per-order commission pressure."
        description="Laundrex is designed around setup plus subscription pricing because per-order laundry commission is usually unattractive for operators."
        features={laundrexFeatures}
      />

      <BusinessPricingPreview />

      <SectionShell background="default">
        <CtaBand
          title="Offer laundry pickup and delivery through Nexivo."
          description="Start with setup from 200 OMR and choose a fixed subscription model instead of per-order commission."
          primaryLabel="Request Demo"
          primaryHref="/business/request-demo"
          secondaryLabel="View Nexivo Laundry"
          secondaryHref="/laundry"
        />
      </SectionShell>
    </PublicPageLayout>
  );
}
