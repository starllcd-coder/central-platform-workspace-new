import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { DataRequestsPanel } from "@/features/privacy/components/data-requests-panel";

export default function DataRequestsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Data Requests"
        title="Access, export, correct, or delete your Nexivo data."
        description="Prepared for GDPR-style privacy requests before Nexivo expands into European markets."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container">
          <DataRequestsPanel />
        </div>
      </section>
    </PublicPageLayout>
  );
}
