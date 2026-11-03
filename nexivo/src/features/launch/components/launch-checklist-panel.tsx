import { CheckCircle2, Clock, Rocket, TriangleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { launchChecklist } from "@/features/launch/data/launch-checklist";

export function LaunchChecklistPanel() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="mb-10 text-center">
          <p className="eyebrow mb-5 justify-center">Launch Readiness</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Nexivo website structure is ready for final integration.
          </h2>
          <p className="mx-auto mt-4 max-w-3xl text-base leading-8 text-slate-600">
            The website now includes customer booking, business marketing, dashboards, privacy,
            localization, integrations, admin monitoring, and growth modules.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {launchChecklist.map((section) => {
            const Icon =
              section.status === "ready"
                ? CheckCircle2
                : section.status === "pending"
                  ? TriangleAlert
                  : Clock;

            return (
              <article
                key={section.title}
                className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                    <Icon size={21} />
                  </div>

                  <Badge
                    variant={
                      section.status === "ready"
                        ? "success"
                        : section.status === "pending"
                          ? "warning"
                          : "secondary"
                    }
                  >
                    {section.status}
                  </Badge>
                </div>

                <h3 className="mt-5 font-heading text-xl font-semibold text-luxury-ink">
                  {section.title}
                </h3>

                <ul className="mt-4 space-y-3">
                  {section.items.map((item) => (
                    <li key={item} className="flex gap-3 text-sm leading-6 text-slate-600">
                      <Rocket size={16} className="mt-1 shrink-0 text-brand-700" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
