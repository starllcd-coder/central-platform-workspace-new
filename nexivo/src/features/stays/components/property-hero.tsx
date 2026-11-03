import { MapPin, ShieldCheck, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { StayProperty } from "@/features/stays/types/stays.types";
import { propertyTypeLabels } from "@/features/stays/data/stay-labels";

type PropertyHeroProps = {
  property: StayProperty;
};

export function PropertyHero({ property }: PropertyHeroProps) {
  return (
    <section className="bg-luxury-gradient">
      <div className="nexivo-container py-10 md:py-14">
        <div className="grid gap-6 lg:grid-cols-[1fr_0.8fr]">
          <div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">{propertyTypeLabels[property.type]}</Badge>
              {property.verified ? (
                <Badge variant="success">
                  <ShieldCheck className="mr-1" size={13} />
                  Verified
                </Badge>
              ) : null}
              {property.featured ? <Badge variant="gold">Featured</Badge> : null}
            </div>

            <h1 className="mt-5 font-heading text-4xl font-semibold tracking-tight text-luxury-ink md:text-6xl">
              {property.name}
            </h1>

            <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-slate-600">
              <span className="inline-flex items-center gap-2">
                <MapPin size={17} />
                {property.area}, {property.city}, {property.country}
              </span>

              <span className="inline-flex items-center gap-2 font-semibold text-slate-700">
                <Star size={17} className="fill-luxury-gold text-luxury-gold" />
                {property.rating} ({property.reviewCount} reviews)
              </span>
            </div>

            <p className="mt-6 max-w-3xl text-base leading-8 text-slate-600">
              {property.shortDescription}
            </p>
          </div>

          <div className="rounded-4xl border border-white/70 bg-white/70 p-3 shadow-premium backdrop-blur-xl">
            <div className="grid h-full min-h-[320px] gap-3 overflow-hidden rounded-3xl md:grid-cols-2">
              <img
                src={property.imageUrl}
                alt={property.name}
                className="h-full min-h-[320px] w-full object-cover md:col-span-2"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
