import { BarChart3, MapPin, Megaphone, WalletCards } from "lucide-react";

const items = [
  {
    title: "Placement control",
    description: "Homepage, search top, destination pages, and category pages can have separate sponsored slots.",
    icon: Megaphone
  },
  {
    title: "City pricing",
    description: "Sponsored prices can vary by GCC city, season, category, and demand.",
    icon: MapPin
  },
  {
    title: "Business billing",
    description: "Sponsored placements can be added to partner invoices or subscription plans.",
    icon: WalletCards
  },
  {
    title: "Performance tracking",
    description: "Businesses should see impressions, clicks, leads, bookings, and return on promotion.",
    icon: BarChart3
  }
];

export function SponsoredListingRulesSection() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-10">
          <p className="eyebrow mb-5">Sponsored Listings</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Future advertising revenue without confusing customers.
          </h2>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
            Sponsored listings should be clearly controlled from DSS Central Platform and should not replace organic quality signals.
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