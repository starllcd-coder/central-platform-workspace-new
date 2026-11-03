import { Car, Hotel, Shirt } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { DestinationGuide } from "@/features/destinations/types/destination.types";

type DestinationCrossSellSectionProps = {
  destination: DestinationGuide;
};

export function DestinationCrossSellSection({ destination }: DestinationCrossSellSectionProps) {
  const cards = [
    {
      title: `Find stays in ${destination.city}`,
      description: "Hotels, apartments, villas, serviced residences, and property booking flow.",
      href: destination.staySearchPath,
      icon: Hotel
    },
    {
      title: `Rent cars in ${destination.city}`,
      description: "Airport pickup, city pickup, SUVs, economy cars, luxury vehicles, and rental terms.",
      href: destination.carSearchPath,
      icon: Car
    },
    {
      title: `Laundry in ${destination.city}`,
      description: "Pickup, delivery, wash, iron, dry cleaning, and hotel guest laundry services.",
      href: destination.laundrySearchPath,
      icon: Shirt
    }
  ];

  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-8 text-center">
          <p className="eyebrow mb-5 justify-center">One Journey</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Complete your {destination.city} trip with Nexivo.
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-base leading-8 text-slate-600">
            A strong destination page should cross-sell accommodation, mobility, and convenience
            services without confusing the customer.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-3">
          {cards.map((card) => {
            const Icon = card.icon;

            return (
              <article
                key={card.title}
                className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-luxury-ink text-white shadow-soft">
                  <Icon size={24} />
                </div>

                <h3 className="mt-6 font-heading text-2xl font-semibold text-luxury-ink">
                  {card.title}
                </h3>

                <p className="mt-3 text-sm leading-7 text-slate-600">{card.description}</p>

                <Button asChild variant="luxury" className="mt-6">
                  <a href={card.href}>Search Now</a>
                </Button>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
