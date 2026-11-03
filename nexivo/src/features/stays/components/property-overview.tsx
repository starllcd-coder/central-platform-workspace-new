import { CheckCircle2 } from "lucide-react";
import type { StayProperty } from "@/features/stays/types/stays.types";
import { stayAmenityLabels } from "@/features/stays/data/stay-labels";

type PropertyOverviewProps = {
  property: StayProperty;
};

export function PropertyOverview({ property }: PropertyOverviewProps) {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container grid gap-8 lg:grid-cols-[1fr_360px]">
        <div>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink">
            Property overview
          </h2>

          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
            {property.shortDescription} Nexivo property pages are prepared for full galleries,
            cancellation policies, guest rules, location maps, verified reviews, and future
            destination-based cross-selling with DriveSphere and Laundrex.
          </p>

          <div className="mt-8 grid gap-3 md:grid-cols-2">
            {property.amenities.map((amenity) => (
              <div
                key={amenity}
                className="flex items-center gap-3 rounded-3xl border border-slate-200 bg-white px-4 py-3 shadow-soft"
              >
                <CheckCircle2 size={18} className="text-emerald-600" />
                <span className="text-sm font-semibold text-slate-700">
                  {stayAmenityLabels[amenity]}
                </span>
              </div>
            ))}
          </div>
        </div>

        <aside className="h-fit rounded-4xl border border-slate-200 bg-luxury-mist p-6 shadow-soft">
          <h3 className="font-heading text-xl font-semibold text-luxury-ink">
            Booking policies
          </h3>

          <div className="mt-5 space-y-4 text-sm leading-6 text-slate-600">
            <p>
              <strong className="text-luxury-ink">Pay at property:</strong>{" "}
              {property.payAtProperty ? "Available" : "Not available"}
            </p>
            <p>
              <strong className="text-luxury-ink">Free cancellation:</strong>{" "}
              {property.freeCancellation ? "Available on selected rooms" : "Not available"}
            </p>
            <p>
              <strong className="text-luxury-ink">Card guarantee:</strong> May be required depending
              on property policy and selected payment option.
            </p>
          </div>
        </aside>
      </div>
    </section>
  );
}
