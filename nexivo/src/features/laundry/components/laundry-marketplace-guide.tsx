import { CalendarClock, CreditCard, MapPin, Shirt } from "lucide-react";

const items = [
  {
    title: "Choose provider",
    description: "Search laundry businesses by city, area, service type, pickup, and delivery options.",
    icon: MapPin
  },
  {
    title: "Select services",
    description: "Choose wash, fold, iron, dry cleaning, express, or hotel guest services.",
    icon: Shirt
  },
  {
    title: "Schedule pickup",
    description: "Set pickup date, time slot, pickup address, and delivery address.",
    icon: CalendarClock
  },
  {
    title: "Pay flexibly",
    description: "Support pay online or pay-on-delivery while keeping business pricing subscription-based.",
    icon: CreditCard
  }
];

export function LaundryMarketplaceGuide() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-10">
          <p className="eyebrow mb-5">Laundrex Flow</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Laundry pickup and delivery for travelers.
          </h2>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
            Laundrex pages are prepared for service catalogs, pickup slots, order tracking, provider operations, and subscription-based business pricing.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-4">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.title} className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
                <Icon size={24} className="text-brand-700" />
                <h3 className="mt-5 font-heading text-xl font-semibold text-luxury-ink">{item.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{item.description}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}