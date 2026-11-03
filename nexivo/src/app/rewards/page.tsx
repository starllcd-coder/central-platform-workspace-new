import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { LoyaltyTiersGrid } from "@/features/growth/components/loyalty-tiers-grid";
import { CouponsGrid } from "@/features/growth/components/coupons-grid";
import { GrowthRulesPanel } from "@/features/growth/components/growth-rules-panel";

export default function RewardsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Nexivo Rewards"
        title="Earn loyalty points across stays, cars, and laundry."
        description="Nexivo rewards can encourage repeat bookings, referrals, verified reviews, and multi-service customer journeys."
      />

      <LoyaltyTiersGrid />
      <CouponsGrid />
      <GrowthRulesPanel />
    </PublicPageLayout>
  );
}