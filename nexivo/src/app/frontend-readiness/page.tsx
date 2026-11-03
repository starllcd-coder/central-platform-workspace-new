import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";

import { FrontendReadinessPanel } from "@/features/qa/components/frontend-readiness-panel";
import { ResponsiveAuditPanel } from "@/features/qa/components/responsive-audit-panel";
import { RtlReadinessPanel } from "@/features/qa/components/rtl-readiness-panel";
import { AccessibilityPanel } from "@/features/qa/components/accessibility-panel";

export default function FrontendReadinessPage() {
  return (
    <PublicPageLayout>

      <PageHero
        eyebrow="Frontend QA"
        title="Nexivo Frontend Readiness"
        description="Final frontend review before real backend and marketplace integrations."
      />

      <FrontendReadinessPanel />

      <ResponsiveAuditPanel />

      <RtlReadinessPanel />

      <AccessibilityPanel />

    </PublicPageLayout>
  );
}