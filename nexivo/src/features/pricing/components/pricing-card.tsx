import { CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { PricingPlan } from "@/features/pricing/types/pricing.types";

type PricingCardProps = {
  plan: PricingPlan;
};

export function PricingCard({ plan }: PricingCardProps) {
  return (
    <article className="flex h-full flex-col rounded-4xl border border-slate-200 bg-white p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Badge variant={plan.product === "laundrex" ? "gold" : "luxury"}>
            {plan.productName}
          </Badge>

          <h3 className="mt-5 font-heading text-2xl font-semibold tracking-tight text-luxury-ink">
            {plan.title}
          </h3>

          <p className="mt-3 text-sm leading-7 text-slate-600">
            {plan.publicDescription}
          </p>
        </div>
      </div>

      <div className="mt-6 rounded-4xl bg-luxury-mist p-5">
        <p className="text-sm font-semibold text-slate-500">Setup Fee</p>
        <div className="mt-1 font-heading text-3xl font-semibold text-luxury-ink">
          {plan.setupFee}
        </div>

        <p className="mt-4 text-sm font-semibold text-slate-500">Ongoing Model</p>
        <p className="mt-1 text-sm font-semibold text-brand-700">
          {plan.ongoingModel}
        </p>
      </div>

      <div className="mt-6 space-y-3">
        {plan.highlights.map((highlight) => (
          <div key={highlight} className="flex gap-3 text-sm leading-6 text-slate-700">
            <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-emerald-600" />
            <span>{highlight}</span>
          </div>
        ))}
      </div>

      <p className="mt-6 rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-600">
        Recommended for: {plan.recommendedFor}
      </p>

      <div className="mt-auto pt-6">
        <Button asChild variant="luxury" fullWidth>
          <a href={`/business/request-demo?product=${plan.product}`}>
            Request Custom Proposal
          </a>
        </Button>
      </div>
    </article>
  );
}
