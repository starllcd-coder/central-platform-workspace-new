"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { stayAmenityLabels, propertyTypeLabels } from "@/features/stays/data/stay-labels";
import { useStaySearchStore } from "@/features/stays/store/stay-search.store";
import type { PropertyAmenity, PropertyType } from "@/features/stays/types/stays.types";

const propertyTypes = Object.keys(propertyTypeLabels) as PropertyType[];
const amenities = Object.keys(stayAmenityLabels) as PropertyAmenity[];

export function StayFilters() {
  const {
    propertyTypes: selectedTypes,
    amenities: selectedAmenities,
    payAtProperty,
    freeCancellation,
    togglePropertyType,
    toggleAmenity,
    togglePayAtProperty,
    toggleFreeCancellation,
    resetFilters
  } = useStaySearchStore();

  return (
    <aside className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft">
      <div className="flex items-center justify-between gap-4">
        <h2 className="font-heading text-xl font-semibold text-luxury-ink">Filters</h2>
        <Button variant="ghost" size="sm" onClick={resetFilters}>
          Reset
        </Button>
      </div>

      <div className="mt-6 space-y-7">
        <section>
          <h3 className="text-sm font-bold uppercase tracking-[0.16em] text-slate-500">
            Property Type
          </h3>

          <div className="mt-3 flex flex-wrap gap-2">
            {propertyTypes.map((type) => (
              <button key={type} onClick={() => togglePropertyType(type)}>
                <Badge variant={selectedTypes.includes(type) ? "luxury" : "outline"}>
                  {propertyTypeLabels[type]}
                </Badge>
              </button>
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-sm font-bold uppercase tracking-[0.16em] text-slate-500">
            Amenities
          </h3>

          <div className="mt-3 flex flex-wrap gap-2">
            {amenities.map((amenity) => (
              <button key={amenity} onClick={() => toggleAmenity(amenity)}>
                <Badge variant={selectedAmenities.includes(amenity) ? "luxury" : "outline"}>
                  {stayAmenityLabels[amenity]}
                </Badge>
              </button>
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-sm font-bold uppercase tracking-[0.16em] text-slate-500">
            Booking Options
          </h3>

          <div className="mt-3 space-y-3">
            <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
              <input
                type="checkbox"
                checked={Boolean(payAtProperty)}
                onChange={togglePayAtProperty}
                className="h-4 w-4 rounded border-slate-300 text-brand-600"
              />
              Pay at property
            </label>

            <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
              <input
                type="checkbox"
                checked={Boolean(freeCancellation)}
                onChange={toggleFreeCancellation}
                className="h-4 w-4 rounded border-slate-300 text-brand-600"
              />
              Free cancellation
            </label>
          </div>
        </section>
      </div>
    </aside>
  );
}
