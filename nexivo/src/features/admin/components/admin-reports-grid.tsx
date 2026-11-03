import { FileBarChart } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AdminReport } from "@/features/admin/types/admin.types";
import { getStatusBadgeVariant } from "@/features/admin/utils/admin-utils";

type AdminReportsGridProps = {
  reports: AdminReport[];
};

export function AdminReportsGrid({ reports }: AdminReportsGridProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Admin Reports</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Reports prepared for marketplace, finance, partner, customer, and compliance monitoring.
        </p>
      </CardHeader>

      <CardContent className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {reports.map((report) => (
          <article
            key={report.id}
            className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <FileBarChart size={21} />
              </div>

              <Badge variant={getStatusBadgeVariant(report.status)}>
                {report.status}
              </Badge>
            </div>

            <p className="mt-5 text-xs font-bold uppercase tracking-[0.16em] text-brand-700">
              {report.category} • {report.frequency}
            </p>

            <h3 className="mt-2 font-heading text-xl font-semibold text-luxury-ink">
              {report.title}
            </h3>

            <p className="mt-3 text-sm leading-7 text-slate-600">{report.description}</p>
          </article>
        ))}
      </CardContent>
    </Card>
  );
}
