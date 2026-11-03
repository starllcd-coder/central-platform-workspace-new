import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { MetricCard } from "@/components/stats/metric-card";
import { businessHeroMetrics } from "@/features/business/data/business-marketing-data";

type BusinessMarketingHeroProps = {
  eyebrow: string;
  title: string;
  description: string;
  primaryLabel?: string;
  primaryHref?: string;
  secondaryLabel?: string;
  secondaryHref?: string;
};

export function BusinessMarketingHero({
  eyebrow,
  title,
  description,
  primaryLabel = "Request Demo",
  primaryHref = "/business/request-demo",
  secondaryLabel = "View Pricing",
  secondaryHref = "/pricing"
}: BusinessMarketingHeroProps) {
  return (
    <section className="relative overflow-hidden bg-midnight-gradient text-white">
      <div className="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-brand-500/20 blur-3xl" />
      <div className="absolute -bottom-32 right-0 h-96 w-96 rounded-full bg-luxury-gold/20 blur-3xl" />

      <div className="nexivo-container relative py-20 md:py-28">
        <div className="max-w-5xl">
          <p className="mb-5 inline-flex rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-semibold text-white/80">
            {eyebrow}
          </p>

          <h1 className="font-heading text-5xl font-semibold tracking-tight md:text-7xl">
            {title}
          </h1>

          <p className="mt-6 max-w-3xl text-lg leading-8 text-white/72">
            {description}
          </p>

          <div className="mt-9 flex flex-wrap gap-3">
            <Button asChild variant="gold" size="lg">
              <a href={primaryHref}>
                {primaryLabel}
                <ArrowRight className="ml-2" size={18} />
              </a>
            </Button>

            <Button asChild variant="outline" size="lg" className="border-white/20 bg-white/10 text-white hover:bg-white/15">
              <a href={secondaryHref}>{secondaryLabel}</a>
            </Button>
          </div>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {businessHeroMetrics.map((metric) => (
            <MetricCard
              key={metric.label}
              label={metric.label}
              value={metric.value}
              description={metric.description}
              className="bg-white/90"
            />
          ))}
        </div>
      </div>
    </section>
  );
}
