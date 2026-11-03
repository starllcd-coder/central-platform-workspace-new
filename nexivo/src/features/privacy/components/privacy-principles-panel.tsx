import { CheckCircle2, ShieldCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { privacyPrinciples } from "@/features/privacy/data/privacy-data";

export function PrivacyPrinciplesPanel() {
  return (
    <Card variant="premium">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
            <ShieldCheck size={22} />
          </div>
          <div>
            <CardTitle>Privacy Principles</CardTitle>
            <p className="mt-1 text-sm text-slate-600">
              Nexivo should be built with privacy, consent, and future European expansion in mind.
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="grid gap-3 md:grid-cols-2">
        {privacyPrinciples.map((item) => (
          <div
            key={item}
            className="flex items-center gap-3 rounded-3xl border border-slate-200 bg-white px-4 py-3 shadow-soft"
          >
            <CheckCircle2 size={18} className="shrink-0 text-emerald-600" />
            <span className="text-sm font-medium text-slate-700">{item}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
