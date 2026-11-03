import { CalendarCheck2, Car, Hotel, Shirt, ShieldCheck, Sparkles } from "lucide-react";

const benefits = [
  {
    title: "One Nexivo account",
    description: "Customers can use one account for stays, car rentals, laundry, rewards, documents, and notifications.",
    icon: Sparkles
  },
  {
    title: "Verified marketplace",
    description: "StayLux properties, DriveSphere vehicles, and Laundrex providers can be verified before publishing.",
    icon: ShieldCheck
  },
  {
    title: "Connected travel journey",
    description: "Book a stay, rent a car, and schedule laundry support from the same destination experience.",
    icon: CalendarCheck2
  }
];

const services = [
  { title: "StayLux", href: "/stays", description: "Hotels, apartments, villas, rooms, units, and pay-at-property flow.", icon: Hotel },
  { title: "DriveSphere", href: "/cars", description: "Car rental listings, vehicle details, pickup flow, and card guarantee.", icon: Car },
  { title: "Laundrex", href: "/laundry", description: "Laundry pickup, delivery, service catalog, and order checkout.", icon: Shirt }
];

export function MarketplaceServiceBenefits() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-10 text-center">
          <p className="eyebrow mb-5 justify-center">Marketplace Completion</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Three services, one premium customer journey.
          </h2>
          <p className="mx-auto mt-4 max-w-3xl text-base leading-8 text-slate-600">
            Nexivo should feel like one complete travel-service platform, not three disconnected apps.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-3">
          {benefits.map((benefit) => {
            const Icon = benefit.icon;
            return (
              <article key={benefit.title} className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
                <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                  <Icon size={24} />
                </div>
                <h3 className="mt-6 font-heading text-2xl font-semibold text-luxury-ink">{benefit.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{benefit.description}</p>
              </article>
            );
          })}
        </div>

        <div className="mt-8 grid gap-5 md:grid-cols-3">
          {services.map((service) => {
            const Icon = service.icon;
            return (
              <a
                key={service.href}
                href={service.href}
                className="group rounded-4xl border border-slate-200 bg-luxury-mist p-6 transition-all hover:-translate-y-1 hover:bg-white hover:shadow-premium"
              >
                <Icon size={26} className="text-brand-700" />
                <h3 className="mt-5 font-heading text-2xl font-semibold text-luxury-ink">{service.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{service.description}</p>
                <p className="mt-5 text-sm font-semibold text-brand-700">Explore {service.title}</p>
              </a>
            );
          })}
        </div>
      </div>
    </section>
  );
}