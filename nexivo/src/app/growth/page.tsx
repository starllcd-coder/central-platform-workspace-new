import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { GrowthOverviewSection } from "@/features/growth/components/growth-overview-section";
import { GrowthRulesPanel } from "@/features/growth/components/growth-rules-panel";

export default function GrowthPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Growth Engine"
        title="Reviews, rewards, coupons, referrals, and sponsored listings."
        description="Nexivo growth features help increase customer retention, business visibility, marketplace trust, and future promotion revenue."
      />

      <GrowthOverviewSection />
      <GrowthRulesPanel />
    </PublicPageLayout>
  );
}