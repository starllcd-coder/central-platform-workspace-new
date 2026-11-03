import { ArrowRight, Building2, ShieldCheck, WalletCards } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SectionShell } from "@/components/layout/section-shell";

const businessHighlights = [
  { label: "DSS Central Platform", icon: Building2 },
  { label: "Dynamic pricing", icon: WalletCards },
  { label: "GCC-first and Europe-ready", icon: ShieldCheck }
] as const;

export function BusinessIntroSection() {
  return (
    <SectionShell background="default" className="bg-luxury-pearl">
      <div className="overflow-hidden rounded-[2rem] border border-luxury-dune/70 bg-white shadow-premium">
        <div className="grid gap-0 lg:grid-cols-[1.15fr_0.85fr] lg:items-stretch">
          <div className="p-7 md:p-10 lg:p-12">
            <p className="mb-5 inline-flex rounded-full border border-luxury-dune bg-luxury-sand/55 px-4 py-2 text-xs font-bold uppercase tracking-[0.16em] text-luxury-bronze">
              For Business
            </p>

            <h2 className="max-w-3xl font-heading text-3xl font-semibold tracking-tight text-luxury-ink md:text-5xl">
              For hotels, car rentals, and laundry businesses.
            </h2>

            <p className="mt-5 max-w-2xl text-base leading-8 text-slate-600">
              Join Nexivo marketplace and manage operations with DSS Central Platform. The full business site covers StayLux, DriveSphere, Laundrex, pricing, demos, and platform controls.
            </p>

            <div className="mt-7 flex flex-col gap-3 sm:flex-row">
              <Button asChild variant="luxury" size="lg">
                <a href="/business">
                  Visit Business
                  <ArrowRight className="ml-2" size={18} />
                </a>
              </Button>

              <Button asChild variant="outline" size="lg" className="border-luxury-dune bg-white">
                <a href="/business/request-demo">Request Demo</a>
              </Button>
            </div>
          </div>

          <div className="bg-midnight-gradient p-6 text-white md:p-8 lg:p-10">
            <div className="grid h-full content-center gap-4">
              {businessHighlights.map((item) => {
                const Icon = item.icon;

                return (
                  <div
                    key={item.label}
                    className="flex items-center gap-4 rounded-2xl border border-white/10 bg-white/10 p-4 shadow-soft backdrop-blur"
                  >
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white/10 text-luxury-dune">
                      <Icon size={20} />
                    </div>
                    <p className="font-semibold text-white/88">{item.label}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </SectionShell>
  );
}
