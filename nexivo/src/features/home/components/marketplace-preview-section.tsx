import { ArrowRight, CheckCircle2 } from "lucide-react";
import {
  marketplacePreviewCards,
  marketplaceTrustItems
} from "@/features/home/data/marketplace-preview-data";
import { SectionHeading } from "@/components/layout/section-heading";
import { SectionShell } from "@/components/layout/section-shell";
import { Button } from "@/components/ui/button";

export function MarketplacePreviewSection() {
  return (
    <SectionShell background="muted" className="bg-[linear-gradient(180deg,#f8fafc_0%,#fffaf0_100%)]">
      <SectionHeading
        eyebrow="Marketplace Ecosystem"
        title="One customer journey across stays, cars, and laundry."
        description="Nexivo connects StayLux, DriveSphere, and Laundrex into one premium booking experience while keeping business operations inside DSS-powered platforms."
        align="center"
      />

      <div className="mt-12 grid gap-6 lg:grid-cols-3">
        {marketplacePreviewCards.map((card) => {
          const Icon = card.icon;

          return (
            <article
              key={card.title}
              className="group overflow-hidden rounded-[1.75rem] border border-luxury-dune/70 bg-white shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium"
            >
              <div className={`relative min-h-40 bg-gradient-to-br ${card.tone} p-6 text-white`}>
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_22%_10%,rgba(255,255,255,.24),transparent_8rem)]" />
                <div className="relative flex items-start justify-between gap-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-white/15 bg-white/15 shadow-soft backdrop-blur-md">
                    <Icon size={25} />
                  </div>

                  <span className="rounded-full border border-white/20 bg-white/15 px-3 py-1 text-xs font-bold uppercase tracking-[0.14em] text-white/85 backdrop-blur">
                    {card.badge}
                  </span>
                </div>

                <div className="relative mt-8">
                  <h3 className="font-heading text-2xl font-semibold tracking-tight">
                    {card.title}
                  </h3>
                  <p className="mt-2 text-sm font-semibold text-luxury-dune">{card.metrics}</p>
                </div>
              </div>

              <div className="p-6">
                <p className="text-sm leading-7 text-slate-600">
                  {card.description}
                </p>

                <div className="mt-5 grid gap-2">
                  {card.features.map((feature) => (
                    <div key={feature} className="flex items-center gap-2 text-sm font-semibold text-slate-700">
                      <CheckCircle2 size={16} className="text-emerald-600" />
                      {feature}
                    </div>
                  ))}
                </div>

                <Button asChild variant="outline" size="md" className="mt-6 w-full border-luxury-dune bg-luxury-pearl/80 group-hover:border-luxury-gold">
                  <a href={card.href}>
                    {card.action}
                    <ArrowRight className="ml-2 transition-transform group-hover:translate-x-1" size={17} />
                  </a>
                </Button>
              </div>
            </article>
          );
        })}
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {marketplaceTrustItems.map((item) => {
          const Icon = item.icon;

          return (
            <div
              key={item.title}
              className="rounded-[1.35rem] border border-white/80 bg-white/80 p-5 shadow-soft backdrop-blur-xl"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-luxury-gold/15 text-luxury-bronze">
                <Icon size={21} />
              </div>

              <h3 className="mt-4 font-heading text-base font-semibold text-luxury-ink">
                {item.title}
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {item.description}
              </p>
            </div>
          );
        })}
      </div>
    </SectionShell>
  );
}
