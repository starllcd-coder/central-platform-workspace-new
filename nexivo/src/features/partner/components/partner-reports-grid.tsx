import { DashboardStatCard } from "@/features/dashboard/components/dashboard-stat-card";

type PartnerReportsGridProps = {
  metrics: readonly {
    label: string;
    value: string;
    description: string;
  }[];
};

export function PartnerReportsGrid({ metrics }: PartnerReportsGridProps) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <DashboardStatCard
          key={metric.label}
          label={metric.label}
          value={metric.value}
          description={metric.description}
        />
      ))}
    </div>
  );
}
