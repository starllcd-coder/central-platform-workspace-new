import { CheckCircle2 } from "lucide-react";
import { authBenefits } from "@/features/auth/data/auth-options";

export function AuthSidePanel() {
  return (
    <aside className="relative hidden overflow-hidden rounded-4xl bg-midnight-gradient p-10 text-white shadow-premium lg:block">
      <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-brand-500/30 blur-3xl" />
      <div className="absolute -bottom-24 -left-24 h-72 w-72 rounded-full bg-luxury-gold/25 blur-3xl" />

      <div className="relative">
        <p className="inline-flex rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-semibold text-white/80">
          Nexivo Account
        </p>

        <h2 className="mt-6 font-heading text-4xl font-semibold tracking-tight">
          One secure profile for your complete travel-service journey.
        </h2>

        <p className="mt-5 text-base leading-8 text-white/72">
          Customers can book stays, rent cars, order laundry, manage rewards, and keep preferences unified across the Nexivo ecosystem.
        </p>

        <div className="mt-10 space-y-4">
          {authBenefits.map((benefit) => (
            <div key={benefit} className="flex gap-3">
              <CheckCircle2 className="mt-0.5 shrink-0 text-luxury-gold" size={20} />
              <span className="text-sm leading-6 text-white/82">{benefit}</span>
            </div>
          ))}
        </div>

        <div className="mt-10 rounded-4xl border border-white/10 bg-white/10 p-5 backdrop-blur">
          <p className="text-sm font-semibold text-white">Powered by DSS Central Platform</p>
          <p className="mt-2 text-sm leading-6 text-white/65">
            Authentication is prepared for centralized customer identity, partner access, SSO, loyalty, billing, and future Europe-ready privacy controls.
          </p>
        </div>
      </div>
    </aside>
  );
}
