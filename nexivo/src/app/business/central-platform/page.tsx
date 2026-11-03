import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";
import { BusinessMarketingHero } from "@/features/business/components/business-marketing-hero";
import { ProductFeaturesSection } from "@/features/business/components/product-features-section";
import { centralPlatformFeatures } from "@/features/business/data/business-marketing-data";

export default function CentralPlatformPage() {
  return (
    <PublicPageLayout>
      <BusinessMarketingHero
        eyebrow="DSS Central Platform"
        title="The control system behind Nexivo, StayLux, DriveSphere, and Laundrex."
        description="DSS Central Platform manages tenants, modules, pricing, commissions, subscriptions, billing, marketplace controls, analytics, countries, currencies, languages, and future Europe-ready expansion."
        primaryLabel="Request Platform Demo"
        primaryHref="/business/request-demo"
      />

      <ProductFeaturesSection
        eyebrow="Central Platform Features"
        title="Keep every commercial rule configurable."
        description="Pricing, commissions, setup fees, subscriptions, countries, languages, taxes, and promotions should be configurable from Central Platform, never hard-coded."
        features={centralPlatformFeatures}
      />

      <SectionShell background="default">
        <CtaBand
          title="Build Nexivo as one ecosystem, not separate products."
          description="The Central Platform should control identity, tenants, billing, pricing, commissions, analytics, notifications, and partner onboarding across all DSS products."
          primaryLabel="Request Demo"
          primaryHref="/business/request-demo"
          secondaryLabel="View Business Section"
          secondaryHref="/business"
        />
      </SectionShell>
    </PublicPageLayout>
  );
}
