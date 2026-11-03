import { CheckCircle2 } from "lucide-react";
import { SectionHeading } from "@/components/layout/section-heading";
import { SectionShell } from "@/components/layout/section-shell";
import { Button } from "@/components/ui/button";

const pricingRows = [
  {
    product: "StayLux",
    setupFee: "From 200 OMR",
    model: "Commission-based",
    display: "Flexible commission after demo"
  },
  {
    product: "DriveSphere",
    setupFee: "From 200 OMR",
    model: "Commission-based",
    display: "Flexible booking commission"
  },
  {
    product: "Laundrex",
    setupFee: "From 200 OMR",
    model: "Subscription-based",
    display: "No order commission required"
  }
];

export function BusinessPricingPreview() {
  return (
    <SectionShell background="muted">
      <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
        <div>
          <SectionHeading
            eyebrow="Pricing Strategy"
            title="Clear starting point, flexible final proposal."
            description="Nexivo should show setup fee and commercial model publicly, but exact commission percentages should remain private for negotiation and future flexibility."
          />

          <div className="mt-8 space-y-3">
            {[
              "Setup fee starts from 200 OMR",
              "StayLux and DriveSphere use commission-based models",
              "Laundrex uses subscription model, not order commission",
              "Exact percentages remain configurable in DSS Central Platform"
            ].map((item) => (
              <div key={item} className="flex items-center gap-3 text-sm font-semibold text-slate-700">
                <CheckCircle2 size={18} className="text-emerald-600" />
                {item}
              </div>
            ))}
          </div>

          <Button asChild variant="luxury" size="lg" className="mt-8">
            <a href="/business/request-demo">Request Custom Proposal</a>
          </Button>
        </div>

        <div className="overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-premium">
          <div className="grid grid-cols-4 bg-luxury-ink px-5 py-4 text-sm font-bold text-white">
            <span>Product</span>
            <span>Setup</span>
            <span>Model</span>
            <span>Public Display</span>
          </div>

          {pricingRows.map((row) => (
            <div
              key={row.product}
              className="grid grid-cols-4 gap-3 border-t border-slate-200 px-5 py-4 text-sm"
            >
              <span className="font-semibold text-luxury-ink">{row.product}</span>
              <span className="text-slate-600">{row.setupFee}</span>
              <span className="text-slate-600">{row.model}</span>
              <span className="text-slate-600">{row.display}</span>
            </div>
          ))}
        </div>
      </div>
    </SectionShell>
  );
}
