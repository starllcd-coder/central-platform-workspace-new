import { Megaphone } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { sponsoredPlacements } from "@/features/growth/data/growth-data";

export function SponsoredPlacementsPanel() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <Card variant="premium">
          <CardHeader>
            <CardTitle>Sponsored Listings & Promotions</CardTitle>
            <p className="text-sm leading-6 text-slate-600">
              Sponsored placements should be managed from DSS Central Platform and priced dynamically by city, category, placement type, and season.
            </p>
          </CardHeader>

          <CardContent className="grid gap-4 md:grid-cols-3">
            {sponsoredPlacements.map((placement) => (
              <div
                key={placement.id}
                className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-luxury-gold/15 text-luxury-bronze">
                  <Megaphone size={22} />
                </div>

                <h3 className="mt-5 font-heading text-xl font-semibold text-luxury-ink">
                  {placement.title}
                </h3>

                <p className="mt-2 text-sm text-slate-600">{placement.businessName}</p>

                <div className="mt-4 flex flex-wrap gap-2">
                  <Badge variant="outline">{placement.serviceScope}</Badge>
                  <Badge variant="secondary">{placement.placement}</Badge>
                  <Badge variant={placement.status === "available" ? "success" : "warning"}>
                    {placement.status}
                  </Badge>
                </div>

                <p className="mt-4 rounded-3xl bg-luxury-mist px-4 py-3 text-sm font-semibold text-slate-700">
                  Monthly price: {placement.monthlyPriceLabel}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
