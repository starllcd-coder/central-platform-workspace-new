import { CheckCircle2 } from "lucide-react";

const rules = [
  "Reviews should be allowed only after completed verified bookings.",
  "Coupons should be validated by service scope, country, expiry, and customer eligibility.",
  "Loyalty points should be earned after booking/order completion, not during pending status.",
  "Referral rewards should be released only after the referred customer or business completes the required action.",
  "Sponsored listings should be controlled from DSS Central Platform with city, service, and placement rules.",
  "Exact promotional pricing and sponsored placement pricing should stay configurable."
];

export function GrowthRulesPanel() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-premium">
          <p className="eyebrow mb-5">Growth Rules</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink">
            Rules to protect trust and revenue.
          </h2>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600">
            These rules keep Nexivo's growth features useful without damaging business margins,
            review credibility, or customer trust.
          </p>

          <div className="mt-8 grid gap-3 md:grid-cols-2">
            {rules.map((rule) => (
              <div
                key={rule}
                className="flex gap-3 rounded-3xl border border-slate-200 bg-luxury-mist px-4 py-3"
              >
                <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-emerald-600" />
                <span className="text-sm font-semibold leading-6 text-slate-700">{rule}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}