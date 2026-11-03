import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";
import { BusinessMarketingHero } from "@/features/business/components/business-marketing-hero";
import { ProductFeaturesSection } from "@/features/business/components/product-features-section";
import { BusinessPricingPreview } from "@/features/business/components/business-pricing-preview";
import { stayLuxFeatures } from "@/features/business/data/business-marketing-data";

export default function BusinessStayLuxPage() {
  return (
    <PublicPageLayout>
      <BusinessMarketingHero
        eyebrow="Nexivo StayLux"
        title="Software and marketplace visibility for hotels and properties."
        description="StayLux supports accommodation booking, property management, owner portal, guest workflows, room inventory, payments, reporting, and Nexivo marketplace listing."
        primaryLabel="Request StayLux Demo"
        primaryHref="/business/request-demo"
      />

      <ProductFeaturesSection
        eyebrow="StayLux Features"
        title="Hospitality operations connected to marketplace demand."
        description="StayLux is designed for hotels, apartments, villas, serviced apartments, and property managers across the GCC."
        features={stayLuxFeatures}
      />

      <BusinessPricingPreview />

      <SectionShell background="default">
        <CtaBand
          title="List your property and manage it with StayLux."
          description="Start with setup from 200 OMR and receive a custom commission-based proposal after demo discussion."
          primaryLabel="Request Demo"
          primaryHref="/business/request-demo"
          secondaryLabel="View Nexivo Stays"
          secondaryHref="/stays"
        />
      </SectionShell>
    </PublicPageLayout>
  );
}
