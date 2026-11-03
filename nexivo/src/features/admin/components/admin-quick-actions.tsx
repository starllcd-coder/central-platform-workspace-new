import { ArrowRight } from "lucide-react";
import { adminQuickActions } from "@/features/admin/components/admin-operations-summary";

export function AdminQuickActions() {
  return (
    <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
      <h2 className="font-heading text-2xl font-semibold text-luxury-ink">Admin Operations</h2>
      <p className="mt-1 text-sm text-slate-600">
        Central monitoring views for Nexivo frontend, marketplace, reports, and audit readiness.
      </p>

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        {adminQuickActions.map((action) => {
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
                View <ArrowRight size={15} className="transition-transform group-hover:translate-x-1" />
              </p>
            </a>
          );
        })}
      </div>
    </div>
  );
}