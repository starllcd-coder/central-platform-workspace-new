import { Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { MonitoringService } from "@/features/admin/types/admin.types";
import { getStatusBadgeVariant } from "@/features/admin/utils/admin-utils";

type MonitoringServicesGridProps = {
  services: MonitoringService[];
};

export function MonitoringServicesGrid({ services }: MonitoringServicesGridProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>System Monitoring</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Monitoring view for marketplace APIs, booking flows, payment layer, Central Platform,
          notification service, and database readiness.
        </p>
      </CardHeader>

      <CardContent className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {services.map((service) => (
          <article
            key={service.id}
            className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <Activity size={21} />
              </div>

              <Badge variant={getStatusBadgeVariant(service.status)}>
                {service.status}
              </Badge>
            </div>

            <p className="mt-5 text-xs font-bold uppercase tracking-[0.16em] text-brand-700">
              {service.area}
            </p>

            <h3 className="mt-2 font-heading text-xl font-semibold text-luxury-ink">
              {service.name}
            </h3>

            <div className="mt-5 space-y-2 text-sm text-slate-600">
              <p>
                <strong className="text-luxury-ink">Uptime:</strong> {service.uptime}
              </p>
              <p>
                <strong className="text-luxury-ink">Latency:</strong> {service.latency}
              </p>
              <p>
                <strong className="text-luxury-ink">Checked:</strong> {service.lastChecked}
              </p>
            </div>
          </article>
        ))}
      </CardContent>
    </Card>
  );
}
