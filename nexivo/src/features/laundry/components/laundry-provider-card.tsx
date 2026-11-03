import { Heart, MapPin, ShieldCheck, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { LaundryProvider } from "@/features/laundry/types/laundry.types";
import { formatMoney } from "@/features/currency/utils/currency-utils";

type LaundryProviderCardProps = {
  provider: LaundryProvider;
};

export function LaundryProviderCard({ provider }: LaundryProviderCardProps) {
  return (
    <article className="group overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium">
      <div className="relative h-64 overflow-hidden">
        <img
          src={provider.imageUrl}
          alt={provider.name}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />

        <div className="absolute left-4 top-4 flex flex-wrap gap-2">
          {provider.featured ? <Badge variant="gold">Featured</Badge> : null}
          {provider.verified ? (
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
          {provider.pickupAvailable ? <Badge variant="secondary">Pickup</Badge> : null}
          {provider.deliveryAvailable ? <Badge variant="secondary">Delivery</Badge> : null}
          <Badge variant="outline">Min {formatMoney(provider.minimumOrder, provider.currency)}</Badge>
        </div>

        <h3 className="mt-4 font-heading text-2xl font-semibold tracking-tight text-luxury-ink">
          {provider.name}
        </h3>

        <div className="mt-3 flex items-center gap-2 text-sm text-slate-600">
          <MapPin size={16} />
          <span>
            {provider.area}, {provider.city}, {provider.country}
          </span>
        </div>

        <p className="mt-4 text-sm leading-7 text-slate-600">{provider.shortDescription}</p>

        <div className="mt-6 flex items-center justify-between gap-4 border-t border-slate-200 pt-5">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
              <Star size={16} className="fill-luxury-gold text-luxury-gold" />
              {provider.rating}
              <span className="text-slate-400">({provider.reviewCount} reviews)</span>
            </div>
            <p className="mt-2 text-sm text-slate-500">Laundry pickup and delivery</p>
          </div>

          <Button asChild variant="luxury">
            <a href={`/laundry/providers/${provider.slug}`}>View</a>
          </Button>
        </div>
      </div>
    </article>
  );
}
