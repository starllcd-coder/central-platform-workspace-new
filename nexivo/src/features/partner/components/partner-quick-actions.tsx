import { ArrowRight } from "lucide-react";
import { partnerQuickActions } from "@/features/partner/components/partner-portal-summary";

export function PartnerQuickActions() {
  return (
    <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
      <h2 className="font-heading text-2xl font-semibold text-luxury-ink">Partner Actions</h2>
      <p className="mt-1 text-sm text-slate-600">
        Business tools prepared for marketplace and DSS Central Platform workflows.
      </p>

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        {partnerQuickActions.map((action) => {
          const Icon = action.icon;

          return (
            <a
              key={action.href}
              href={action.href}
              className="group rounded-3xl border border-slate-200 bg-luxury-mist p-5 transition-all hover:-translate-y-1 hover:bg-white hover:shadow-soft"
            >
              <Icon size={22} className="text-brand-700" />
              <p className="mt-4 font-heading text-lg font-semibold text-luxury-ink">{action.label}</p>
              <p className="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-brand-700">
                Open <ArrowRight size={15} className="transition-transform group-hover:translate-x-1" />
              </p>
            </a>
          );
        })}
      </div>
    </div>
  );
}