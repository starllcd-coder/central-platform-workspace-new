import { FileClock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AuditLogEntry } from "@/features/admin/types/admin.types";

type AuditLogsTableProps = {
  logs: AuditLogEntry[];
};

export function AuditLogsTable({ logs }: AuditLogsTableProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Audit Logs</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Prepared audit trail for customer, partner, admin, system, pricing, consent, and sync events.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {logs.map((log) => (
          <div
            key={log.id}
            className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft lg:grid-cols-[1fr_auto]"
          >
            <div className="flex gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <FileClock size={21} />
              </div>

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                    {log.action}
                  </h3>
                  <Badge variant="outline">{log.actorRole}</Badge>
                </div>

                <p className="mt-1 text-sm leading-6 text-slate-600">{log.description}</p>

                <p className="mt-1 text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
                  {log.actor} • {log.target} • {log.ipAddress}
                </p>
              </div>
            </div>

            <div className="text-sm font-semibold text-slate-500 lg:text-right">
              {log.createdAt}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
