import { Gift, Heart, Megaphone, Star, TicketPercent, UsersRound } from "lucide-react";

const growthItems = [
  {
    title: "Verified Reviews",
    description: "Only completed StayLux, DriveSphere, and Laundrex bookings should generate reviews.",
    href: "/reviews",
    icon: Star
  },
  {
    title: "Wishlist",
    description: "Customers can save stays, cars, laundry providers, and destinations for later.",
    href: "/wishlist",
    icon: Heart
  },
  {
    title: "Rewards",
    description: "Loyalty points encourage repeat bookings across all Nexivo services.",
    href: "/rewards",
    icon: Gift
  },
  {
    title: "Coupons",
    description: "Coupons support launch offers, seasonal campaigns, upgrades, and delivery offers.",
    href: "/coupons",
    icon: TicketPercent
  },
  {
    title: "Referrals",
    description: "Customer and business referrals can reduce acquisition cost and increase trust.",
    href: "/referrals",
    icon: UsersRound
  },
  {
    title: "Promotions",
    description: "Sponsored listings and destination campaigns create future business revenue channels.",
    href: "/promotions",
    icon: Megaphone
  }
];

export function GrowthOverviewSection() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-10 text-center">
          <p className="eyebrow mb-5 justify-center">Growth Engine</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Retention, referrals, offers, and sponsored visibility.
          </h2>
          <p className="mx-auto mt-4 max-w-3xl text-base leading-8 text-slate-600">
            Nexivo growth features are designed to increase repeat bookings, customer trust,
            marketplace activity, and future business advertising revenue.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {growthItems.map((item) => {
            const Icon = item.icon;

            return (
              <a
                key={item.href}
                href={item.href}
                className="group rounded-4xl border border-slate-200 bg-luxury-mist p-6 transition-all hover:-translate-y-1 hover:bg-white hover:shadow-premium"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                  <Icon size={24} />
                </div>
                <h3 className="mt-6 font-heading text-2xl font-semibold text-luxury-ink">
                  {item.title}
                </h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{item.description}</p>
                <p className="mt-5 text-sm font-semibold text-brand-700">Open {item.title}</p>
              </a>
            );
          })}
        </div>
      </div>
    </section>
  );
}