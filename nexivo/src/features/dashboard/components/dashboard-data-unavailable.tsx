import { Card, CardContent } from "@/components/ui/card";
export function DashboardDataUnavailable() {
  return <Card variant="premium"><CardContent className="p-6"><p role="alert" className="text-sm text-slate-600">Live dashboard data is unavailable. Please sign in again or try refreshing this page.</p></CardContent></Card>;
}
