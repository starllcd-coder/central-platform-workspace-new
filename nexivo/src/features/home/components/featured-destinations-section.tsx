import { ArrowRight, MapPin, Star } from "lucide-react";
import { featuredDestinationCards } from "@/features/home/data/marketplace-preview-data";
import { SectionHeading } from "@/components/layout/section-heading";
import { SectionShell } from "@/components/layout/section-shell";
import { Button } from "@/components/ui/button";

export function FeaturedDestinationsSection() {
  return (
    <SectionShell background="default" className="bg-luxury-pearl">
      <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <SectionHeading
          eyebrow="Featured GCC Destinations"
          title="Explore high-demand cities across the GCC."
          description="Nexivo starts with GCC destinations and prepares the same structure for future European expansion."
        />

        <Button asChild variant="outline" size="lg" className="shrink-0 border-luxury-dune bg-white/85">
          <a href="/destinations">
            View All Destinations
            <ArrowRight className="ml-2" size={18} />
          </a>
        </Button>
      </div>

      <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {featuredDestinationCards.map((destination) => (
          <a
            key={destination.slug}
            href={`/destinations/${destination.slug}`}
            className="group overflow-hidden rounded-[1.65rem] border border-luxury-dune/70 bg-white shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium"
          >
            <div className={`relative min-h-48 overflow-hidden bg-gradient-to-br ${destination.imageGradient}`}>
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_20%,rgba(255,255,255,.35),transparent_8rem)]" />
              <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-black/55 to-transparent" />

              <div className="absolute left-4 top-4 flex items-center gap-2 rounded-full border border-white/20 bg-white/20 px-3 py-1 text-xs font-bold uppercase tracking-[0.14em] text-white shadow-soft backdrop-blur-md">
                <MapPin size={14} />
                {destination.country}
              </div>

              <div className="absolute right-4 top-4 rounded-full bg-white/90 px-3 py-1 text-xs font-bold text-luxury-ink shadow-soft">
                {destination.stats}
              </div>

              <div className="absolute bottom-5 left-5 right-5">
                <p className="flex items-center gap-2 text-sm font-semibold text-white/80">
                  <Star size={15} className="fill-luxury-gold text-luxury-gold" />
                  Marketplace destination
                </p>
                <h3 className="mt-1 font-heading text-3xl font-semibold tracking-tight text-white">
                  {destination.city}
                </h3>
              </div>
            </div>

            <div className="p-5">
              <p className="text-sm leading-7 text-slate-600">
                {destination.description}
              </p>

              <div className="mt-5 flex flex-wrap gap-2">
                {destination.highlights.map((item) => (
                  <span
                    key={item}
                    className="rounded-full border border-luxury-dune bg-luxury-sand/45 px-3 py-1 text-xs font-semibold text-slate-700"
                  >
                    {item}
                  </span>
                ))}
              </div>

              <div className="mt-6 inline-flex items-center text-sm font-bold text-luxury-bronze">
                Explore {destination.city}
                <ArrowRight className="ml-2 transition-transform group-hover:translate-x-1" size={17} />
              </div>
            </div>
          </a>
        ))}
      </div>
    </SectionShell>
  );
}
