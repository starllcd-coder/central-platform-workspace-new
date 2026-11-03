import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { ReferralPanel } from "@/features/engagement/components/referral-panel";
import { ReferralGrowthSection } from "@/features/engagement/components/referral-growth-section";

export default function ReferralsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Referrals"
        title="Grow Nexivo through customer and business referrals."
        description="Referral rewards can increase customer acquisition and business onboarding across GCC markets."
      />

      <ReferralPanel />
      <ReferralGrowthSection />
    </PublicPageLayout>
  );
}