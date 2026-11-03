import { ArrowRight, Car, CheckCircle2, Hotel, MapPin, Shirt } from "lucide-react";
import { Button } from "@/components/ui/button";
import { BookingSearchPanel } from "@/features/booking/components/booking-search-panel";
import { homeStats, trustBadges } from "@/features/home/data/home-data";

export function HomeHero() {
  return (
    <section className="relative overflow-hidden bg-[linear-gradient(135deg,#fffdf8_0%,#f8fafc_46%,#f4ead7_100%)]">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-luxury-gold/50 to-transparent" />
      <div className="absolute left-0 top-16 h-72 w-72 rounded-full bg-brand-500/10 blur-3xl" />
      <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-luxury-gold/20 blur-3xl" />

      <div className="nexivo-container relative py-8 md:py-10 lg:py-12">
        <div className="relative">
          <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <p className="eyebrow border-luxury-gold/40 bg-white/80 text-luxury-bronze shadow-soft">
              Stays, cars, and laundry across the GCC
            </p>

            <a
              href="/business"
              className="inline-flex w-fit items-center rounded-full border border-luxury-dune bg-white/78 px-4 py-2 text-sm font-semibold text-slate-600 shadow-soft transition-colors hover:text-luxury-bronze"
            >
              Are you a business? Join Nexivo
            </a>
          </div>

          <h1 className="max-w-5xl font-heading text-4xl font-semibold leading-[1.04] tracking-tight text-luxury-ink sm:text-5xl lg:text-6xl">
            Book stays, rent cars, and order laundry in one refined marketplace.
          </h1>

          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600 md:text-lg">
            Nexivo unifies StayLux, DriveSphere, and Laundrex into a premium GCC booking experience for travelers, residents, and businesses preparing for Europe-ready growth.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            {[
              { label: "StayLux stays", icon: Hotel },
              { label: "DriveSphere cars", icon: Car },
              { label: "Laundrex laundry", icon: Shirt }
            ].map((item) => {
              const Icon = item.icon;

              return (
                <span
                  key={item.label}
                  className="inline-flex items-center gap-2 rounded-full border border-luxury-dune bg-white/78 px-4 py-2 text-sm font-semibold text-slate-700 shadow-soft"
                >
                  <Icon size={16} className="text-luxury-bronze" />
                  {item.label}
                </span>
              );
            })}
          </div>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Button asChild variant="luxury" size="xl" className="shadow-premium">
              <a href="#search-nexivo">
                Search Nexivo
                <ArrowRight className="ml-2" size={18} />
              </a>
            </Button>
          </div>
        </div>

        <div id="search-nexivo" className="mt-7 min-w-0 scroll-mt-28 overflow-hidden rounded-[2rem] border border-white/80 bg-white/55 p-3 shadow-premium backdrop-blur-xl md:p-4">
          <div className="relative mb-4 overflow-hidden rounded-[1.5rem] bg-midnight-gradient p-4 text-white md:p-5">
            <div className="absolute inset-0 opacity-70 [background:radial-gradient(circle_at_20%_25%,rgba(255,255,255,.18),transparent_12rem),radial-gradient(circle_at_85%_10%,rgba(200,164,93,.35),transparent_11rem)]" />
            <div className="relative grid gap-5 lg:grid-cols-[1fr_auto] lg:items-center">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-luxury-dune">
                  Marketplace preview
                </p>
                <h2 className="mt-2 max-w-2xl font-heading text-2xl font-semibold tracking-tight md:text-3xl">
                  Dubai weekend, airport car, hotel laundry.
                </h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-white/72">
                  One journey stitched across Nexivo services and DSS-ready operations.
                </p>
              </div>

              <div className="grid grid-cols-3 gap-2 lg:w-[28rem]">
                {[
                  { label: "Stay", icon: Hotel },
                  { label: "Car", icon: MapPin },
                  { label: "Laundry", icon: Shirt }
                ].map((item) => {
                  const Icon = item.icon;

                  return (
                    <div key={item.label} className="rounded-2xl border border-white/10 bg-white/10 p-3 text-center">
                      <Icon className="mx-auto text-luxury-dune" size={18} />
                      <p className="mt-1 text-xs font-semibold text-white/85">{item.label}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="min-w-0 overflow-hidden">
            <BookingSearchPanel />
          </div>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {homeStats.map((stat) => (
            <div
              key={stat.label}
              className="min-w-0 rounded-[1.4rem] border border-white/80 bg-white/80 p-4 shadow-soft backdrop-blur-xl"
            >
              <div className="font-heading text-2xl font-semibold text-luxury-ink md:text-3xl">
                {stat.value}
              </div>
              <div className="mt-1 text-sm font-semibold text-slate-700">{stat.label}</div>
              <p className="mt-2 text-xs leading-5 text-slate-500">{stat.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {trustBadges.slice(0, 4).map((badge) => (
            <span
              key={badge}
              className="inline-flex items-center justify-center gap-2 rounded-full border border-white/80 bg-white/70 px-4 py-2 text-sm font-semibold text-slate-700 shadow-soft backdrop-blur"
            >
              <CheckCircle2 size={16} className="text-emerald-600" />
              {badge}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
