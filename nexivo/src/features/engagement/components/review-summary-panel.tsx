import { ShieldCheck, Star } from "lucide-react";
import { verifiedReviews } from "@/features/engagement/data/engagement-data";

export function ReviewSummaryPanel() {
  const average =
    verifiedReviews.reduce((sum, review) => sum + review.rating, 0) / verifiedReviews.length;

  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-premium">
          <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
            <div>
              <p className="eyebrow mb-5">Trust Score</p>
              <h2 className="font-heading text-4xl font-semibold text-luxury-ink">
                {average.toFixed(1)} / 5.0
              </h2>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                Nexivo review architecture should prioritize verified booking reviews only.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-3xl bg-luxury-mist p-5">
                <Star size={22} className="fill-luxury-gold text-luxury-gold" />
                <p className="mt-3 font-heading text-2xl font-semibold text-luxury-ink">
                  {verifiedReviews.length}
                </p>
                <p className="text-sm text-slate-600">Sample verified reviews</p>
              </div>

              <div className="rounded-3xl bg-luxury-mist p-5">
                <ShieldCheck size={22} className="text-emerald-600" />
                <p className="mt-3 font-heading text-2xl font-semibold text-luxury-ink">100%</p>
                <p className="text-sm text-slate-600">Linked to completed bookings</p>
              </div>

              <div className="rounded-3xl bg-luxury-mist p-5">
                <Star size={22} className="text-brand-700" />
                <p className="mt-3 font-heading text-2xl font-semibold text-luxury-ink">3</p>
                <p className="text-sm text-slate-600">Stay, car, and laundry coverage</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}