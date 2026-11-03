import { CheckCircle2, PlugZap, TriangleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getLiveConnectors } from "@/lib/integrations/live-connectors";

export async function IntegrationStatusPanel() {
  const integrationConnectors = await getLiveConnectors();
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Integration Layer</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Nexivo is prepared to connect customer marketplace flows with DSS Central Platform,
          payment gateways, billing, notifications, analytics, and privacy workflows.
        </p>
      </CardHeader>

      <CardContent className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {integrationConnectors.map((connector) => {
          const ready = connector.status === "connected";

          return (
            <article
              key={connector.id}
              className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                  <PlugZap size={21} />
                </div>

                <Badge
                  variant={
                    connector.status === "connected"
                      ? "success"
                      : connector.status === "mock"
                        ? "warning"
                        : connector.status === "planned"
                          ? "secondary"
                          : "destructive"
                  }
                >
                  {connector.status}
                </Badge>
              </div>

              <p className="mt-5 text-xs font-bold uppercase tracking-[0.16em] text-brand-700">
                {connector.module}
              </p>

              <h3 className="mt-2 font-heading text-xl font-semibold text-luxury-ink">
                {connector.name}
              </h3>

              <p className="mt-3 text-sm leading-7 text-slate-600">{connector.description}</p>

              <div className="mt-5 flex items-center gap-2 text-sm font-semibold text-slate-600">
                {ready ? (
                  <CheckCircle2 size={18} className="text-emerald-600" />
                ) : (
                  <TriangleAlert size={18} className="text-amber-600" />
                )}
                {connector.requiredForLaunch ? "Required for launch" : "Optional / phase-ready"}
              </div>

              <p className="mt-3 rounded-2xl bg-slate-50 px-3 py-2 text-xs font-mono text-slate-500">
                {connector.endpoint}
              </p>
            </article>
          );
        })}
      </CardContent>
    </Card>
  );
}
