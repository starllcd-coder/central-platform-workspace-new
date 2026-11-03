import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { customerQuickActions } from "@/features/customer/components/customer-portal-summary";

export function CustomerQuickActions() {
  return (
    <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-heading text-2xl font-semibold text-luxury-ink">Quick Actions</h2>
          <p className="mt-1 text-sm text-slate-600">Continue your Nexivo journey faster.</p>
        </div>
        <Button asChild variant="outline">
          <a href="/destinations">Explore Destinations</a>
        </Button>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        {customerQuickActions.map((action) => {
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
                Continue <ArrowRight size={15} className="transition-transform group-hover:translate-x-1" />
              </p>
            </a>
          );
        })}
      </div>
    </div>
  );
}