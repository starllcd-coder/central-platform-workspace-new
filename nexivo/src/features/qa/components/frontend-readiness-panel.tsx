import { CheckCircle2 } from "lucide-react";
import { frontendReadiness } from "@/features/qa/data/frontend-readiness";

export function FrontendReadinessPanel() {
  return (
    <section className="section-padding bg-white">

      <div className="nexivo-container">

        <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-premium">

          <p className="eyebrow mb-5">
            Frontend Status
          </p>

          <h2 className="font-heading text-3xl font-semibold text-luxury-ink">
            Frontend Completion Status
          </h2>

          <div className="mt-8 grid gap-4 md:grid-cols-2">

            {frontendReadiness.map((item) => (

              <div
                key={item.area}
                className="flex items-center gap-3 rounded-3xl border border-slate-200 bg-luxury-mist px-4 py-4"
              >

                <CheckCircle2
                  size={18}
                  className="text-emerald-600"
                />

                <span className="font-semibold text-slate-700">
                  {item.area}
                </span>

              </div>

            ))}

          </div>

        </div>

      </div>

    </section>
  );
}