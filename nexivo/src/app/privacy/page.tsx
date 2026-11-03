import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { PrivacyPrinciplesPanel } from "@/features/privacy/components/privacy-principles-panel";
import { DataRequestsPanel } from "@/features/privacy/components/data-requests-panel";

export default function PrivacyPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Privacy"
        title="Privacy and data protection."
        description="Nexivo is designed with privacy, consent, customer data controls, and Europe-ready GDPR principles."
        primaryLabel="Manage Cookies"
        primaryHref="/cookie-center"
        secondaryLabel="Data Requests"
        secondaryHref="/data-requests"
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container space-y-8">
          <PrivacyPrinciplesPanel />
          <DataRequestsPanel />
        </div>
      </section>
    </PublicPageLayout>
  );
}
