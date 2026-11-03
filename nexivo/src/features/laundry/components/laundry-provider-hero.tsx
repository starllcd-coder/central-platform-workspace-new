import { MapPin, ShieldCheck, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { LaundryProvider } from "@/features/laundry/types/laundry.types";

type LaundryProviderHeroProps = {
  provider: LaundryProvider;
};

export function LaundryProviderHero({ provider }: LaundryProviderHeroProps) {
  return (
    <section className="bg-luxury-gradient">
      <div className="nexivo-container py-10 md:py-14">
        <div className="grid gap-6 lg:grid-cols-[1fr_0.8fr]">
          <div>
            <div className="flex flex-wrap gap-2">
              {provider.verified ? (
                <Badge variant="success">
                  <ShieldCheck className="mr-1" size={13} />
                  Verified Provider
                </Badge>
              ) : null}
              {provider.featured ? <Badge variant="gold">Featured</Badge> : null}
              {provider.pickupAvailable ? <Badge variant="secondary">Pickup Available</Badge> : null}
              {provider.deliveryAvailable ? <Badge variant="secondary">Delivery Available</Badge> : null}
            </div>

            <h1 className="mt-5 font-heading text-4xl font-semibold tracking-tight text-luxury-ink md:text-6xl">
              {provider.name}
            </h1>

            <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-slate-600">
              <span className="inline-flex items-center gap-2">
                <MapPin size={17} />
                {provider.area}, {provider.city}, {provider.country}
              </span>

              <span className="inline-flex items-center gap-2 font-semibold text-slate-700">
                <Star size={17} className="fill-luxury-gold text-luxury-gold" />
                {provider.rating} ({provider.reviewCount} reviews)
              </span>
            </div>

            <p className="mt-6 max-w-3xl text-base leading-8 text-slate-600">
              {provider.shortDescription}
            </p>
          </div>

          <div className="rounded-4xl border border-white/70 bg-white/70 p-3 shadow-premium backdrop-blur-xl">
            <img
              src={provider.imageUrl}
              alt={provider.name}
              className="h-full min-h-[360px] w-full rounded-3xl object-cover"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
