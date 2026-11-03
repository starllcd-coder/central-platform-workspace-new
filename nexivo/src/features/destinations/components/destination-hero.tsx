import { Car, Hotel, MapPin, Shirt, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { DestinationGuide } from "@/features/destinations/types/destination.types";

type DestinationHeroProps = {
  destination: DestinationGuide;
};

export function DestinationHero({ destination }: DestinationHeroProps) {
  return (
    <section className="relative overflow-hidden bg-midnight-gradient text-white">
      <img
        src={destination.heroImage}
        alt={destination.city}
        className="absolute inset-0 h-full w-full object-cover opacity-25"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-luxury-ink via-luxury-ink/85 to-luxury-ink/40" />

      <div className="nexivo-container relative py-20 md:py-28">
        <div className="max-w-5xl">
          <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-semibold text-white/80">
            <MapPin size={16} />
            {destination.city}, {destination.country}
          </p>

          <h1 className="font-heading text-5xl font-semibold tracking-tight md:text-7xl">
            {destination.headline}
          </h1>

          <p className="mt-6 max-w-3xl text-lg leading-8 text-white/72">
            {destination.description}
          </p>

          <div className="mt-8 flex flex-wrap gap-2">
            {destination.bestFor.map((item) => (
              <Badge key={item} variant="gold">
                <Star className="mr-1" size={13} />
                {item}
              </Badge>
            ))}
          </div>

          <div className="mt-9 flex flex-wrap gap-3">
            <Button asChild variant="gold" size="lg">
              <a href={destination.staySearchPath}>
                <Hotel className="mr-2" size={18} />
                Search Stays
              </a>
            </Button>

            <Button asChild variant="outline" size="lg" className="border-white/20 bg-white/10 text-white hover:bg-white/15">
              <a href={destination.carSearchPath}>
                <Car className="mr-2" size={18} />
                Search Cars
              </a>
            </Button>

            <Button asChild variant="outline" size="lg" className="border-white/20 bg-white/10 text-white hover:bg-white/15">
              <a href={destination.laundrySearchPath}>
                <Shirt className="mr-2" size={18} />
                Laundry
              </a>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
