import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { ConsentCenterPanel } from "@/features/privacy/components/consent-center-panel";

export default function ConsentPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Consent"
        title="Control how Nexivo uses optional data."
        description="Consent settings are prepared for analytics, marketing, personalization, third-party integrations, and future GDPR readiness."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container">
          <ConsentCenterPanel />
        </div>
      </section>
    </PublicPageLayout>
  );
}
