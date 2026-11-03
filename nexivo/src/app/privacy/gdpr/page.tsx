import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { DataRequestsPanel } from "@/features/privacy/components/data-requests-panel";
import { ConsentCenterPanel } from "@/features/privacy/components/consent-center-panel";

export default function GdprPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="GDPR Requests"
        title="Data export, deletion, and consent controls."
        description="Future GDPR-ready privacy controls for customer data export, deletion, correction, consent, and account privacy preferences."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container space-y-8">
          <DataRequestsPanel />
          <ConsentCenterPanel />
        </div>
      </section>
    </PublicPageLayout>
  );
}
