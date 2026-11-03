import { LifeBuoy } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PartnerSupportTicket } from "@/features/partner/types/partner.types";

type PartnerSupportListProps = {
  tickets: PartnerSupportTicket[];
};

export function PartnerSupportList({ tickets }: PartnerSupportListProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Support Tickets</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Business support for onboarding, technical issues, bookings, billing, and marketplace setup.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {tickets.map((ticket) => (
          <div
            key={ticket.id}
            className="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft md:flex-row md:items-center md:justify-between"
          >
            <div className="flex gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <LifeBuoy size={21} />
              </div>

              <div>
                <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                  {ticket.subject}
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  {ticket.category} • {ticket.createdAt}
                </p>
              </div>
            </div>

            <Badge
              variant={
                ticket.status === "resolved"
                  ? "success"
                  : ticket.status === "in-progress"
                    ? "warning"
                    : "outline"
              }
            >
              {ticket.status}
            </Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
