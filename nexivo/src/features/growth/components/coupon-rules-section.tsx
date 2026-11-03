import { BadgePercent, CalendarClock, Globe2, ShieldCheck } from "lucide-react";

const rules = [
  {
    title: "Service scope",
    description: "Coupon can apply to all services or only stays, cars, or laundry.",
    icon: BadgePercent
  },
  {
    title: "Expiry control",
    description: "Campaigns should expire automatically based on configured dates.",
    icon: CalendarClock
  },
  {
    title: "Country rules",
    description: "Coupons can be limited by GCC country, city, or future Europe market.",
    icon: Globe2
  },
  {
    title: "Abuse prevention",
    description: "Limit coupon usage by account, phone, email, booking status, and payment status.",
    icon: ShieldCheck
  }
];

export function CouponRulesSection() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-10">
          <p className="eyebrow mb-5">Coupon Engine</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Coupon rules prepared for real backend validation.
          </h2>
        </div>

        <div className="grid gap-5 md:grid-cols-4">
          {rules.map((rule) => {
            const Icon = rule.icon;

            return (
              <article key={rule.title} className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
                <Icon size={24} className="text-brand-700" />
                <h3 className="mt-5 font-heading text-xl font-semibold text-luxury-ink">{rule.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{rule.description}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}