import { DatabaseZap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { dataRequestTypes } from "@/features/privacy/data/privacy-data";

export function DataRequestsPanel() {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Data Requests</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Prepared for GDPR-style access, export, deletion, correction, restriction, and consent
          withdrawal workflows.
        </p>
      </CardHeader>

      <CardContent className="grid gap-5 md:grid-cols-2">
        {dataRequestTypes.map((request) => (
          <article
            key={request.id}
            className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <DatabaseZap size={21} />
              </div>

              <Badge variant="outline">{request.status}</Badge>
            </div>

            <h3 className="mt-5 font-heading text-xl font-semibold text-luxury-ink">
              {request.title}
            </h3>

            <p className="mt-3 text-sm leading-7 text-slate-600">{request.description}</p>

            <Button variant="outline" className="mt-5">
              Start Request
            </Button>
          </article>
        ))}
      </CardContent>
    </Card>
  );
}
