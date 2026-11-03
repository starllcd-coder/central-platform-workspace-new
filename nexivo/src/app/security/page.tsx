import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { SecurityControlsPanel } from "@/features/privacy/components/security-controls-panel";

export default function SecurityPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Security"
        title="Security controls for customer and business trust."
        description="Nexivo security design covers account access, payments, business tenants, documents, data requests, and compliance preparation."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container">
          <SecurityControlsPanel />
        </div>
      </section>
    </PublicPageLayout>
  );
}
