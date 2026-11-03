import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { PromotionsGrid } from "@/features/growth/components/promotions-grid";
import { SponsoredListingRulesSection } from "@/features/growth/components/sponsored-listing-rules-section";
import { SponsoredPlacementsPanel } from "@/features/growth/components/sponsored-placements-panel";

export default function PromotionsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Promotions"
        title="Seasonal offers and sponsored marketplace visibility."
        description="Nexivo promotions support customer campaigns and business sponsored placements across destinations, search pages, and categories."
      />

      <PromotionsGrid />
      <SponsoredPlacementsPanel />
      <SponsoredListingRulesSection />
    </PublicPageLayout>
  );
}