import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { NotificationPreferencesPanel } from "@/features/notifications/components/notification-preferences-panel";
import { NotificationLogsList } from "@/features/notifications/components/notification-logs-list";

export default function NotificationsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Notifications"
        title="Nexivo communication center."
        description="Booking updates, payment alerts, reminders, promotions, security messages, and business updates across email, SMS, WhatsApp, and push."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container space-y-8">
          <NotificationPreferencesPanel />
          <NotificationLogsList />
        </div>
      </section>
    </PublicPageLayout>
  );
}
