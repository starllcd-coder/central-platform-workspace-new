import { BedDouble, CalendarDays, CreditCard, ShieldCheck } from "lucide-react";

const items = [
  {
    title: "Choose destination",
    description: "Search by GCC city, area, property name, or future campaign destination.",
    icon: CalendarDays
  },
  {
    title: "Compare rooms",
    description: "Review property details, room/unit types, amenities, policies, and rates.",
    icon: BedDouble
  },
  {
    title: "Secure booking",
    description: "Continue with pay online or pay-at-property card guarantee flow.",
    icon: CreditCard
  },
  {
    title: "Verified stay",
    description: "Future workflow can connect booking confirmation, reviews, rewards, and documents.",
    icon: ShieldCheck
  }
];

export function StayMarketplaceGuide() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-10">
          <p className="eyebrow mb-5">StayLux Flow</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            A premium stay-booking journey.
          </h2>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
            StayLux pages are prepared for real inventory, room availability, payment guarantees, cancellation rules, and owner/admin sync.
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