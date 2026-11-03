import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";
import { BusinessMarketingHero } from "@/features/business/components/business-marketing-hero";
import { ProductFeaturesSection } from "@/features/business/components/product-features-section";
import { BusinessPricingPreview } from "@/features/business/components/business-pricing-preview";
import { driveSphereFeatures } from "@/features/business/data/business-marketing-data";

export default function BusinessDriveSpherePage() {
  return (
    <PublicPageLayout>
      <BusinessMarketingHero
        eyebrow="Nexivo DriveSphere"
        title="Car rental software and marketplace booking channel."
        description="DriveSphere supports web operations, admin/staff mobile app workflows, customer booking app, fleet management, rentals, payments, documents, and Nexivo marketplace listings."
        primaryLabel="Request DriveSphere Demo"
        primaryHref="/business/request-demo"
      />

      <ProductFeaturesSection
        eyebrow="DriveSphere Features"
        title="Fleet operations connected to booking demand."
        description="DriveSphere is designed for car rental businesses, fleet operators, branches, staff users, and customer booking workflows."
        features={driveSphereFeatures}
      />

      <BusinessPricingPreview />

      <SectionShell background="default">
        <CtaBand
          title="List your fleet and manage rentals with DriveSphere."
          description="Start with setup from 200 OMR and receive a custom commission-based proposal after demo discussion."
          primaryLabel="Request Demo"
          primaryHref="/business/request-demo"
          secondaryLabel="View Nexivo Cars"
          secondaryHref="/cars"
        />
      </SectionShell>
    </PublicPageLayout>
  );
}
