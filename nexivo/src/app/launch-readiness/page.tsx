import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { LaunchChecklistPanel } from "@/features/launch/components/launch-checklist-panel";
import { QaChecklistPanel } from "@/features/launch/components/qa-checklist-panel";

export default function LaunchReadinessPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Launch Readiness"
        title="Final Nexivo website readiness checklist."
        description="Use this page to review what is ready, what is mock-ready, and what still needs real integration before production launch."
      />

      <LaunchChecklistPanel />
      <QaChecklistPanel />
    </PublicPageLayout>
  );
}
