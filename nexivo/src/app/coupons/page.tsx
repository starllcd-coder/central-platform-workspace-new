import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { CouponRulesSection } from "@/features/growth/components/coupon-rules-section";
import { CouponsGrid } from "@/features/growth/components/coupons-grid";

export default function CouponsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Coupons"
        title="Save on Nexivo stays, cars, and laundry."
        description="Coupons are prepared for percentage discounts, fixed discounts, delivery offers, upgrades, and future loyalty personalization."
      />

      <CouponsGrid />
      <CouponRulesSection />
    </PublicPageLayout>
  );
}