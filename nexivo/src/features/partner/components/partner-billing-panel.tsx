import { FileText, WalletCards } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PartnerInvoice } from "@/features/partner/types/partner.types";

type PartnerBillingPanelProps = {
  invoices: PartnerInvoice[];
};

export function PartnerBillingPanel({ invoices }: PartnerBillingPanelProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Billing & Invoices</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Setup fees, subscriptions, commissions, sponsored placements, and DSS Central Platform billing.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="rounded-4xl bg-midnight-gradient p-6 text-white shadow-premium">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-white/10 text-luxury-gold">
              <WalletCards size={25} />
            </div>

            <div>
              <p className="text-sm text-white/65">Current commercial model</p>
              <h3 className="font-heading text-2xl font-semibold">
                Setup + commission/subscription
              </h3>
              <p className="mt-1 text-sm text-white/65">
                Exact percentages remain configurable inside DSS Central Platform.
              </p>
            </div>
          </div>
        </div>

        {invoices.map((invoice) => (
          <div
            key={invoice.id}
            className="flex items-center justify-between rounded-3xl border border-slate-200 bg-white p-4 shadow-soft"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-50 text-brand-700">
                <FileText size={19} />
              </div>

              <div>
                <h3 className="font-semibold text-luxury-ink">{invoice.title}</h3>
                <p className="text-sm text-slate-500">Due {invoice.dueDate}</p>
              </div>
            </div>

            <div className="text-right">
              <p className="font-heading text-lg font-semibold text-luxury-ink">
                {invoice.amount}
              </p>
              <Badge
                variant={
                  invoice.status === "paid"
                    ? "success"
                    : invoice.status === "unpaid"
                      ? "warning"
                      : "destructive"
                }
              >
                {invoice.status}
              </Badge>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
