import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type DashboardStatCardProps = {
  label: string;
  value: string;
  description: string;
};

export function DashboardStatCard({ label, value, description }: DashboardStatCardProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <p className="text-sm font-semibold text-slate-500">{label}</p>
        <CardTitle className="text-4xl">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-6 text-slate-600">{description}</p>
      </CardContent>
    </Card>
  );
}
