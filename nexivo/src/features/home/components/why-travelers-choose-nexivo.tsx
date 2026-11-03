import { BadgeCheck, CreditCard, Globe2, Languages, ShieldCheck, UserRoundCheck } from "lucide-react";

const items = [
  {
    title: "One Nexivo Account",
    description: "Use one profile for stays, cars, laundry, documents, rewards, and notifications.",
    icon: UserRoundCheck
  },
  {
    title: "Verified Businesses",
    description: "Hotels, fleets, and laundry providers can be verified before marketplace publishing.",
    icon: BadgeCheck
  },
  {
    title: "Secure Booking",
    description: "Prepared for card guarantees, payment gateways, account security, and audit logs.",
    icon: ShieldCheck
  },
  {
    title: "Flexible Payments",
    description: "Pay online, pay at hotel, pay at pickup, or pay on delivery based on service rules.",
    icon: CreditCard
  },
  {
    title: "Multi-Currency",
    description: "GCC currencies are prepared first, with EUR and GBP ready for future expansion.",
    icon: Globe2
  },
  {
    title: "English + Arabic",
    description: "Designed for GCC customers with RTL-ready Arabic and future European languages.",
    icon: Languages
  }
];

export function WhyTravelersChooseNexivo() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-10 text-center">
          <p className="eyebrow mb-5 justify-center">Why Nexivo</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Why travelers choose Nexivo.
          </h2>
          <p className="mx-auto mt-4 max-w-3xl text-base leading-8 text-slate-600">
            Nexivo is built for travelers who want convenience, clarity, trust, and premium service across the GCC.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {items.map((item) => {
            const Icon = item.icon;

            return (
              <article
                key={item.title}
                className="group rounded-4xl border border-luxury-dune/70 bg-[linear-gradient(135deg,#ffffff_0%,#fffaf0_100%)] p-6 shadow-soft transition-all hover:-translate-y-1 hover:shadow-premium"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-brand-50 text-brand-700 transition-transform group-hover:scale-105">
                  <Icon size={24} />
                </div>
                <h3 className="mt-6 font-heading text-2xl font-semibold text-luxury-ink">
                  {item.title}
                </h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{item.description}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}