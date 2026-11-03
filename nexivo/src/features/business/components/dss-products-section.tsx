import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SectionHeading } from "@/components/layout/section-heading";
import { SectionShell } from "@/components/layout/section-shell";
import { dssProductCards } from "@/features/business/data/business-marketing-data";

export function DssProductsSection() {
  return (
    <SectionShell background="default">
      <SectionHeading
        eyebrow="DSS Product Ecosystem"
        title="Business software connected to the Nexivo marketplace."
        description="Each product can operate as a SaaS platform while also feeding inventory and services into the Nexivo customer marketplace."
        align="center"
      />

      <div className="mt-12 grid gap-6 lg:grid-cols-2">
        {dssProductCards.map((product) => {
          const Icon = product.icon;

          return (
            <article
              key={product.title}
              className="group rounded-4xl border border-slate-200 bg-white p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium"
            >
              <div className="flex flex-wrap items-start justify-between gap-5">
                <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-luxury-ink text-white shadow-soft">
                  <Icon size={24} />
                </div>

                <Badge variant="gold">{product.badge}</Badge>
              </div>

              <h3 className="mt-7 font-heading text-3xl font-semibold tracking-tight text-luxury-ink">
                {product.title}
              </h3>

              <p className="mt-4 text-sm leading-7 text-slate-600">{product.description}</p>

              <div className="mt-5 flex flex-wrap gap-2">
                {product.highlights.map((highlight) => (
                  <Badge key={highlight} variant="outline">
                    {highlight}
                  </Badge>
                ))}
              </div>

              <p className="mt-5 rounded-3xl bg-luxury-mist px-4 py-3 text-sm font-semibold text-slate-700">
                {product.pricing}
              </p>

              <Button asChild variant="outline" className="mt-6">
                <a href={product.href}>
                  Learn More
                  <ArrowRight className="ml-2 transition-transform group-hover:translate-x-1" size={17} />
                </a>
              </Button>
            </article>
          );
        })}
      </div>
    </SectionShell>
  );
}
