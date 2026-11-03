import { ArrowDownRight, ArrowRight, ArrowUpRight, Minus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AdminMetric } from "@/features/admin/types/admin.types";
import { getTrendLabel } from "@/features/admin/utils/admin-utils";

type AdminMetricsGridProps = {
  metrics: AdminMetric[];
};

export function AdminMetricsGrid({ metrics }: AdminMetricsGridProps) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => {
        const TrendIcon =
          metric.trend === "up" ? ArrowUpRight : metric.trend === "down" ? ArrowDownRight : Minus;

        return (
          <Card key={metric.label} variant="premium">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-slate-500">{metric.label}</p>
                  <CardTitle className="mt-2 text-4xl">{metric.value}</CardTitle>
                </div>

                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-50 text-brand-700">
                  <TrendIcon size={20} />
                </div>
              </div>
            </CardHeader>

            <CardContent>
              <p className="text-sm leading-6 text-slate-600">{metric.description}</p>
              <p className="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-brand-700">
                {getTrendLabel(metric.trend)}
                <ArrowRight size={15} />
              </p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
