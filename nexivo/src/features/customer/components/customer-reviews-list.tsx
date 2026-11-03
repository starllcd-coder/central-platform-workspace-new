import { Star } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CustomerReview } from "@/features/customer/types/customer.types";

type CustomerReviewsListProps = {
  reviews: CustomerReview[];
};

export function CustomerReviewsList({ reviews }: CustomerReviewsListProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Verified Reviews</CardTitle>
        <p className="text-sm text-slate-600">
          Reviews connected only to completed verified bookings.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {reviews.map((review) => (
          <div
            key={review.id}
            className="rounded-3xl border border-slate-200 bg-white p-4 shadow-soft"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                  {review.title}
                </h3>
                <p className="mt-1 text-sm text-slate-500">{review.date}</p>
              </div>

              <div className="flex items-center gap-1 text-luxury-gold">
                {Array.from({ length: review.rating }).map((_, index) => (
                  <Star key={index} size={15} className="fill-luxury-gold" />
                ))}
              </div>
            </div>

            <p className="mt-4 text-sm leading-6 text-slate-600">{review.comment}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
