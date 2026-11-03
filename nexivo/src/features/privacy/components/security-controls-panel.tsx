import { ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { securityControls } from "@/features/privacy/data/privacy-data";

export function SecurityControlsPanel() {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Security Controls</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Security checklist for customer accounts, payments, business tenants, document vault, and
          Europe-ready compliance.
        </p>
      </CardHeader>

      <CardContent className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {securityControls.map((control) => (
          <article
            key={control.id}
            className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <ShieldCheck size={21} />
              </div>

              <Badge variant={control.status === "ready" ? "success" : "warning"}>
                {control.status}
              </Badge>
            </div>

            <p className="mt-5 text-xs font-bold uppercase tracking-[0.16em] text-brand-700">
              {control.area}
            </p>

            <h3 className="mt-2 font-heading text-xl font-semibold text-luxury-ink">
              {control.title}
            </h3>

            <p className="mt-3 text-sm leading-7 text-slate-600">{control.description}</p>
          </article>
        ))}
      </CardContent>
    </Card>
  );
}
