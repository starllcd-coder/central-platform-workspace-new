import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { NotificationPreferencesPanel } from "@/features/notifications/components/notification-preferences-panel";
import { NotificationTemplatesGrid } from "@/features/notifications/components/notification-templates-grid";

export default function NotificationSettingsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Notification Settings"
        title="Configure customer and business communication preferences."
        description="Notification settings are prepared for customer preferences and DSS Central Platform template management."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container space-y-8">
          <NotificationPreferencesPanel />
          <NotificationTemplatesGrid />
        </div>
      </section>
    </PublicPageLayout>
  );
}
