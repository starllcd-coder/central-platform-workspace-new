import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { ConsentCenterPanel } from "@/features/privacy/components/consent-center-panel";
import { PrivacyPrinciplesPanel } from "@/features/privacy/components/privacy-principles-panel";

export default function CookieCenterPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Cookie Center"
        title="Manage cookies and consent preferences."
        description="Control optional analytics, marketing, personalization, and third-party integrations while keeping necessary Nexivo functionality enabled."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container space-y-8">
          <ConsentCenterPanel />
          <PrivacyPrinciplesPanel />
        </div>
      </section>
    </PublicPageLayout>
  );
}
