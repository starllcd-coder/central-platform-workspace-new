import { FileText, ShieldCheck, TriangleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CustomerDocument } from "@/features/customer/types/customer.types";

type CustomerDocumentsListProps = {
  documents: CustomerDocument[];
};

export function CustomerDocumentsList({ documents }: CustomerDocumentsListProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Travel Document Vault</CardTitle>
        <p className="text-sm text-slate-600">
          Secure document area prepared for passport, ID, and driving license workflows.
        </p>
      </CardHeader>

      <CardContent className="space-y-3">
        {documents.map((document) => {
          const Icon = document.status === "expired" ? TriangleAlert : ShieldCheck;

          return (
            <div
              key={document.id}
              className="flex items-center justify-between rounded-3xl border border-slate-200 bg-white p-4 shadow-soft"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-50 text-brand-700">
                  <FileText size={19} />
                </div>

                <div>
                  <h3 className="font-semibold text-luxury-ink">{document.title}</h3>
                  <p className="text-sm text-slate-500">Updated {document.updatedAt}</p>
                </div>
              </div>

              <Badge
                variant={
                  document.status === "verified"
                    ? "success"
                    : document.status === "pending"
                      ? "warning"
                      : "destructive"
                }
              >
                <Icon className="mr-1" size={13} />
                {document.status}
              </Badge>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
