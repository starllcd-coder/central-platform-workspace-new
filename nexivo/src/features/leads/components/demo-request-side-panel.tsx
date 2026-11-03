import { CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const leadWorkflow = [
  "Lead created in DSS Central Platform",
  "Product interest assigned",
  "Demo scheduled",
  "Custom proposal prepared",
  "Setup fee and commercial model confirmed",
  "Tenant onboarding started"
];

export function DemoRequestSidePanel() {
  return (
    <Card variant="dark">
      <CardHeader>
        <CardTitle>What happens after request?</CardTitle>
        <p className="text-sm leading-6 text-white/65">
          Nexivo business leads should become structured sales opportunities inside DSS Central Platform.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {leadWorkflow.map((item) => (
          <div key={item} className="flex gap-3 text-sm leading-6 text-white/80">
            <CheckCircle2 className="mt-0.5 shrink-0 text-luxury-gold" size={18} />
            <span>{item}</span>
          </div>
        ))}

        <div className="rounded-3xl border border-white/10 bg-white/10 p-4">
          <p className="text-sm font-semibold text-white">Pricing reminder</p>
          <p className="mt-2 text-sm leading-6 text-white/65">
            Public website should not display exact commission percentages. Keep them flexible and configurable.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
