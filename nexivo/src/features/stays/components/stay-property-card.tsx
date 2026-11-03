import { Heart, MapPin, ShieldCheck, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { StayProperty } from "@/features/stays/types/stays.types";
import { propertyTypeLabels } from "@/features/stays/data/stay-labels";
import { formatMoney } from "@/features/currency/utils/currency-utils";

type StayPropertyCardProps = {
  property: StayProperty;
};

export function StayPropertyCard({ property }: StayPropertyCardProps) {
  return (
    <article className="group overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium">
      <div className="relative h-64 overflow-hidden">
        <img
          src={property.imageUrl}
          alt={property.name}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />

        <div className="absolute left-4 top-4 flex flex-wrap gap-2">
          {property.featured ? <Badge variant="gold">Featured</Badge> : null}
          {property.verified ? (
            <Badge variant="success">
              <ShieldCheck className="mr-1" size={13} />
              Verified
            </Badge>
          ) : null}
        </div>

        <button className="absolute right-4 top-4 flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-slate-700 shadow-soft transition-colors hover:text-red-500">
          <Heart size={18} />
        </button>
      </div>

      <div className="p-6">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline">{propertyTypeLabels[property.type]}</Badge>
          {property.payAtProperty ? <Badge variant="secondary">Pay at property</Badge> : null}
          {property.freeCancellation ? <Badge variant="secondary">Free cancellation</Badge> : null}
        </div>

        <h3 className="mt-4 font-heading text-2xl font-semibold tracking-tight text-luxury-ink">
          {property.name}
        </h3>

        <div className="mt-3 flex items-center gap-2 text-sm text-slate-600">
          <MapPin size={16} />
          <span>
            {property.area}, {property.city}, {property.country}
          </span>
        </div>

        <p className="mt-4 text-sm leading-7 text-slate-600">
          {property.shortDescription}
        </p>

        <div className="mt-5 flex items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
              <Star size={16} className="fill-luxury-gold text-luxury-gold" />
              {property.rating}
              <span className="text-slate-400">({property.reviewCount} reviews)</span>
            </div>

            <div className="mt-2">
              <span className="font-heading text-2xl font-semibold text-luxury-ink">
                {formatMoney(property.pricePerNight, property.currency)}
              </span>
              <span className="text-sm text-slate-500"> / night</span>
            </div>
          </div>

          <Button asChild variant="luxury">
            <a href={`/stays/${property.slug}`}>View</a>
          </Button>
        </div>
      </div>
    </article>
  );
}
