import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { IntegrationStatusPanel } from "@/features/integrations/components/integration-status-panel";

export default function IntegrationsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Integrations"
        title="Nexivo integration layer and Central Platform connectors."
        description="Mock endpoints and connector contracts are prepared for marketplace inventory, bookings, leads, payments, billing, notifications, analytics, and privacy workflows."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container">
          <IntegrationStatusPanel />
        </div>
      </section>
    </PublicPageLayout>
  );
}
