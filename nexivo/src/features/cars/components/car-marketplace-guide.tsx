import { BadgeCheck, CalendarDays, Car, CreditCard } from "lucide-react";

const items = [
  {
    title: "Search rental cars",
    description: "Filter vehicles by city, airport, category, transmission, and booking terms.",
    icon: Car
  },
  {
    title: "Review policies",
    description: "Show deposit, mileage, fuel, insurance, minimum age, and document requirements.",
    icon: BadgeCheck
  },
  {
    title: "Reserve vehicle",
    description: "Support pay online or pay-at-pickup with secure card guarantee.",
    icon: CreditCard
  },
  {
    title: "Pickup-ready flow",
    description: "Future staff app can manage pickup, return, damage checks, and rental agreement.",
    icon: CalendarDays
  }
];

export function CarMarketplaceGuide() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-10">
          <p className="eyebrow mb-5">DriveSphere Flow</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Car rental designed for clear terms.
          </h2>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
            DriveSphere pages are prepared for real fleet inventory, branch operations, deposits, driver documents, and staff mobile workflow.
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