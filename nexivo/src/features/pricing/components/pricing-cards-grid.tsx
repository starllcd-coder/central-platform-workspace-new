import { PricingCard } from "@/features/pricing/components/pricing-card";
import { pricingPlans } from "@/features/pricing/data/pricing-data";
import { cn } from "@/lib/utils";

type PricingCardsGridProps = {
  className?: string;
};

export function PricingCardsGrid({ className }: PricingCardsGridProps) {
  return (
    <section className={cn("section-padding bg-luxury-mist", className)}>
      <div className="nexivo-container">
        <div className="grid gap-6 lg:grid-cols-3">
          {pricingPlans.map((plan) => (
            <PricingCard key={plan.id} plan={plan} />
          ))}
        </div>

        <div className="mt-8 rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
          <h3 className="font-heading text-2xl font-semibold text-luxury-ink">
            Important pricing note
          </h3>
          <p className="mt-3 text-sm leading-7 text-slate-600">
            Nexivo should not publicly display exact commission percentages. Public pricing should
            show starting setup fee and commercial model. Final pricing should be discussed after
            demo and configured dynamically from DSS Central Platform.
          </p>
        </div>
      </div>
    </section>
  );
}
