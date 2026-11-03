import { CheckCircle2 } from "lucide-react";
import { qaChecklist } from "@/features/launch/data/launch-checklist";

export function QaChecklistPanel() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-premium">
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink">
            Final QA checklist
          </h2>

          <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600">
            Before launch, run these checks and connect real integrations where required.
          </p>

          <div className="mt-8 grid gap-3 md:grid-cols-2">
            {qaChecklist.map((item) => (
              <div
                key={item}
                className="flex items-center gap-3 rounded-3xl border border-slate-200 bg-luxury-mist px-4 py-3"
              >
                <CheckCircle2 size={18} className="shrink-0 text-emerald-600" />
                <span className="text-sm font-semibold text-slate-700">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
