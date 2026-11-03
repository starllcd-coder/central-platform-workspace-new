import { BarChart3, Bell, Building2, CreditCard, DatabaseZap, Hotel, Layers3, PlugZap, Shirt, WalletCards, Car } from "lucide-react";

const apps = [
  { title: "StayLux", description: "Hotels, apartments, villas, rooms, and owner portal.", icon: Hotel },
  { title: "DriveSphere", description: "Fleet, branches, staff workflow, and car rental bookings.", icon: Car },
  { title: "Laundrex", description: "Laundry providers, pickup, delivery, and service catalogs.", icon: Shirt }
];

const controls = [
  { label: "Tenants", icon: Building2 },
  { label: "Pricing", icon: WalletCards },
  { label: "Billing", icon: CreditCard },
  { label: "Analytics", icon: BarChart3 },
  { label: "Integrations", icon: PlugZap },
  { label: "Notifications", icon: Bell }
];

export function DssEcosystemSection() {
  return (
    <section className="section-padding bg-[linear-gradient(180deg,#f8fafc_0%,#fffdf8_100%)]">
      <div className="nexivo-container">
        <div className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
          <div>
            <p className="eyebrow mb-5">DSS Ecosystem</p>
            <h2 className="font-heading text-3xl font-semibold tracking-tight text-luxury-ink md:text-5xl">
              One central platform powering three marketplace apps.
            </h2>
            <p className="mt-5 max-w-2xl text-base leading-8 text-slate-600">
              DSS Central Platform keeps tenant access, pricing, billing, analytics, integrations, and notifications configurable while Nexivo presents a simple premium customer marketplace.
            </p>

            <div className="mt-7 grid gap-3 sm:grid-cols-2">
              {controls.map((control) => {
                const Icon = control.icon;

                return (
                  <div
                    key={control.label}
                    className="flex items-center gap-3 rounded-3xl border border-luxury-dune/70 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-soft"
                  >
                    <Icon size={18} className="text-luxury-bronze" />
                    {control.label}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="relative rounded-[2rem] border border-luxury-dune/70 bg-white p-6 shadow-premium">
            <div className="absolute inset-6 rounded-[1.5rem] bg-[radial-gradient(circle_at_center,rgba(245,197,66,.22),transparent_16rem)]" />

            <div className="relative grid gap-4">
              <div className="mx-auto flex max-w-md items-center justify-center gap-3 rounded-[1.75rem] bg-midnight-gradient p-5 text-white shadow-premium">
                <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-white/10 text-luxury-dune">
                  <DatabaseZap size={25} />
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.16em] text-luxury-dune">
                    Core System
                  </p>
                  <h3 className="font-heading text-2xl font-semibold">DSS Central Platform</h3>
                </div>
              </div>

              <div className="mx-auto h-10 w-px bg-luxury-dune" />

              <div className="grid gap-4 md:grid-cols-3">
                {apps.map((app) => {
                  const Icon = app.icon;

                  return (
                    <article
                      key={app.title}
                      className="rounded-4xl border border-slate-200 bg-[linear-gradient(135deg,#ffffff_0%,#fff9ed_100%)] p-5 text-center shadow-soft"
                    >
                      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                        <Icon size={22} />
                      </div>
                      <h3 className="mt-4 font-heading text-xl font-semibold text-luxury-ink">
                        {app.title}
                      </h3>
                      <p className="mt-2 text-sm leading-6 text-slate-600">{app.description}</p>
                    </article>
                  );
                })}
              </div>

              <div className="mt-2 rounded-4xl border border-dashed border-luxury-dune bg-luxury-mist p-5">
                <div className="flex items-center justify-center gap-3 text-sm font-semibold text-slate-700">
                  <Layers3 size={18} className="text-brand-700" />
                  Multi-tenant SaaS architecture prepared for GCC launch and Europe expansion.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}