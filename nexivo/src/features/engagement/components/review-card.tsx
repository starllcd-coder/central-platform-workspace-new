import { ShieldCheck, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { VerifiedReview } from "@/features/engagement/types/engagement.types";

type ReviewCardProps = {
  review: VerifiedReview;
};

export function ReviewCard({ review }: ReviewCardProps) {
  return (
    <article className="overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-soft">
      {review.imageUrl ? (
        <img src={review.imageUrl} alt={review.title} className="h-44 w-full object-cover" />
      ) : null}

      <div className="p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Badge variant="outline">{review.provider}</Badge>
          {review.verifiedBooking ? (
            <Badge variant="success">
              <ShieldCheck className="mr-1" size={13} />
              Verified booking
            </Badge>
          ) : null}
        </div>

        <h3 className="mt-4 font-heading text-xl font-semibold text-luxury-ink">
          {review.title}
        </h3>

        <div className="mt-3 flex items-center gap-1 text-luxury-gold">
          {Array.from({ length: review.rating }).map((_, index) => (
            <Star key={index} size={16} className="fill-luxury-gold" />
          ))}
        </div>

        <p className="mt-4 text-sm leading-7 text-slate-600">{review.comment}</p>

        <p className="mt-4 text-sm font-semibold text-slate-500">
          {review.customerName} • {review.date}
        </p>
      </div>
    </article>
  );
}
