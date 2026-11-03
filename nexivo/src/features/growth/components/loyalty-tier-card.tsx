import { CheckCircle2, Crown, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { LoyaltyTierInfo } from "@/features/growth/types/growth.types";

type LoyaltyTierCardProps = {
  tier: LoyaltyTierInfo;
  current?: boolean;
};

export function LoyaltyTierCard({ tier, current = false }: LoyaltyTierCardProps) {
  return (
    <article className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium">
      <div className="flex items-start justify-between gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-luxury-gold/15 text-luxury-bronze">
          {tier.tier === "platinum" ? <Crown size={24} /> : <Star size={24} />}
        </div>

        {current ? <Badge variant="success">Current</Badge> : null}
      </div>

      <h3 className="mt-6 font-heading text-2xl font-semibold capitalize text-luxury-ink">
        {tier.title}
      </h3>

      <p className="mt-2 text-sm text-slate-500">
        Required points: {tier.requiredPoints.toLocaleString()}
      </p>

      <p className="mt-4 rounded-3xl bg-luxury-mist px-4 py-3 text-sm font-semibold text-brand-700">
        Earning multiplier: {tier.multiplier}
      </p>

      <div className="mt-5 space-y-3">
        {tier.benefits.map((benefit) => (
          <div key={benefit} className="flex gap-3 text-sm leading-6 text-slate-700">
            <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-emerald-600" />
            <span>{benefit}</span>
          </div>
        ))}
      </div>
    </article>
  );
}
