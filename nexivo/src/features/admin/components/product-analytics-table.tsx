import { BarChart3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ProductAnalytics } from "@/features/admin/types/admin.types";

type ProductAnalyticsTableProps = {
  products: ProductAnalytics[];
};

export function ProductAnalyticsTable({ products }: ProductAnalyticsTableProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Product Analytics</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Performance overview for StayLux, DriveSphere, and Laundrex marketplace operations.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {products.map((product) => (
          <div
            key={product.product}
            className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft lg:grid-cols-[1fr_auto]"
          >
            <div className="flex gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <BarChart3 size={21} />
              </div>

              <div>
                <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                  {product.product}
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  {product.activeListings} active listings
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 text-sm lg:min-w-[420px]">
              <Metric label="Bookings" value={product.bookings.toString()} />
              <Metric label="Revenue" value={product.revenue} />
              <Metric label="Conversion" value={product.conversionRate} />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-slate-50 p-3 text-center">
      <p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">{label}</p>
      <p className="mt-1 font-heading text-lg font-semibold text-luxury-ink">{value}</p>
    </div>
  );
}
