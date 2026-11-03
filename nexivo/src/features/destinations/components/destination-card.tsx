import { ArrowRight, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { DestinationGuide } from "@/features/destinations/types/destination.types";

type DestinationCardProps = {
  destination: DestinationGuide;
};

export function DestinationCard({ destination }: DestinationCardProps) {
  return (
    <article className="group overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium">
      <div className="relative h-56 overflow-hidden">
        <img
          src={destination.heroImage}
          alt={destination.city}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />

        <div className="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-xs font-bold uppercase tracking-[0.14em] text-brand-700 shadow-soft">
          {destination.countryCode}
        </div>
      </div>

      <div className="p-6">
        <p className="flex items-center gap-2 text-sm font-semibold text-slate-500">
          <MapPin size={15} />
          {destination.country}
        </p>

        <h3 className="mt-2 font-heading text-3xl font-semibold text-luxury-ink">
          {destination.city}
        </h3>

        <p className="mt-4 line-clamp-3 text-sm leading-7 text-slate-600">
          {destination.description}
        </p>

        <div className="mt-5 flex flex-wrap gap-2">
          {destination.bestFor.slice(0, 3).map((item) => (
            <span
              key={item}
              className="rounded-full bg-luxury-mist px-3 py-1 text-xs font-semibold text-slate-700"
            >
              {item}
            </span>
          ))}
        </div>

        <Button asChild variant="outline" className="mt-6">
          <a href={`/destinations/${destination.slug}`}>
            Explore {destination.city}
            <ArrowRight className="ml-2 transition-transform group-hover:translate-x-1" size={17} />
          </a>
        </Button>
      </div>
    </article>
  );
}
