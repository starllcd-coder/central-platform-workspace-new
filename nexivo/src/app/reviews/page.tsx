import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { ReviewSummaryPanel } from "@/features/engagement/components/review-summary-panel";
import { ReviewsSection } from "@/features/engagement/components/reviews-section";

export default function ReviewsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Verified Reviews"
        title="Real feedback from completed Nexivo bookings."
        description="Reviews should be connected only to verified StayLux, DriveSphere, and Laundrex transactions to build trust."
      />

      <ReviewSummaryPanel />
      <ReviewsSection />
    </PublicPageLayout>
  );
}