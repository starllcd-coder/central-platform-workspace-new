import { Building2, Car, Hotel, Shirt } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PartnerListing } from "@/features/partner/types/partner.types";
import {
  getPartnerProductBadgeVariant,
  getPartnerProductLabel
} from "@/features/partner/components/partner-utils";

type PartnerListingsTableProps = {
  listings: PartnerListing[];
};

export function PartnerListingsTable({ listings }: PartnerListingsTableProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Business Listings</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Listings connected to StayLux, DriveSphere, Laundrex, and Nexivo marketplace visibility.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {listings.map((listing) => {
          const Icon =
            listing.product === "staylux"
              ? Hotel
              : listing.product === "drivesphere"
                ? Car
                : listing.product === "laundrex"
                  ? Shirt
                  : Building2;

          return (
            <div
              key={listing.id}
              className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft lg:grid-cols-[1fr_auto]"
            >
              <div className="flex gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                  <Icon size={21} />
                </div>

                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                      {listing.title}
                    </h3>
                    <Badge variant={getPartnerProductBadgeVariant(listing.product)}>
                      {getPartnerProductLabel(listing.product)}
                    </Badge>
                    <Badge
                      variant={
                        listing.status === "active"
                          ? "success"
                          : listing.status === "pending"
                            ? "warning"
                            : listing.status === "paused"
                              ? "secondary"
                              : "outline"
                      }
                    >
                      {listing.status}
                    </Badge>
                  </div>

                  <p className="mt-1 text-sm text-slate-600">{listing.location}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 text-sm lg:min-w-[360px]">
                <Metric label="Views" value={listing.views.toLocaleString()} />
                <Metric label="Bookings" value={listing.bookings.toString()} />
                <Metric label="Revenue" value={listing.revenue} />
              </div>
            </div>
          );
        })}
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
