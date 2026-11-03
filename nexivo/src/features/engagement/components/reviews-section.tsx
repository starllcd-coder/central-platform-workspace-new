import { SectionHeading } from "@/components/layout/section-heading";
import { SectionShell } from "@/components/layout/section-shell";
import { ReviewCard } from "@/features/engagement/components/review-card";
import { verifiedReviews } from "@/features/engagement/data/engagement-data";

export function ReviewsSection() {
  return (
    <SectionShell background="default">
      <SectionHeading
        eyebrow="Verified Reviews"
        title="Trust should come from completed bookings only."
        description="Nexivo reviews are designed to be attached to verified StayLux, DriveSphere, and Laundrex bookings."
        align="center"
      />

      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {verifiedReviews.map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </div>
    </SectionShell>
  );
}
