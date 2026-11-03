"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { vehicleCategoryLabels, vehicleFeatureLabels } from "@/features/cars/data/car-labels";
import { useCarSearchStore } from "@/features/cars/store/car-search.store";
import type { VehicleCategory, VehicleFeature } from "@/features/cars/types/cars.types";

const categories = Object.keys(vehicleCategoryLabels) as VehicleCategory[];
const features = Object.keys(vehicleFeatureLabels) as VehicleFeature[];

export function CarFilters() {
  const {
    category,
    features: selectedFeatures,
    transmission,
    freeCancellation,
    payAtPickup,
    toggleCategory,
    toggleFeature,
    setTransmission,
    toggleFreeCancellation,
    togglePayAtPickup,
    resetFilters
  } = useCarSearchStore();

  return (
    <aside id="car-filters" className="scroll-mt-24 rounded-4xl border border-slate-200 bg-white p-5 shadow-soft">
      <div className="flex items-center justify-between gap-4">
        <h2 className="font-heading text-xl font-semibold text-luxury-ink">Filters</h2>
        <Button variant="ghost" size="sm" onClick={resetFilters}>
          Reset
        </Button>
      </div>

      <div className="mt-6 space-y-7">
        <section>
          <h3 className="text-sm font-bold uppercase tracking-[0.16em] text-slate-500">
            Vehicle Category
          </h3>

          <div className="mt-3 flex flex-wrap gap-2">
            {categories.map((item) => (
              <button key={item} onClick={() => toggleCategory(item)}>
                <Badge variant={category.includes(item) ? "luxury" : "outline"}>
                  {vehicleCategoryLabels[item]}
                </Badge>
              </button>
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-sm font-bold uppercase tracking-[0.16em] text-slate-500">
            Transmission
          </h3>

          <div className="mt-3 flex flex-wrap gap-2">
            <button onClick={() => setTransmission(transmission === "automatic" ? undefined : "automatic")}>
              <Badge variant={transmission === "automatic" ? "luxury" : "outline"}>
                Automatic
              </Badge>
            </button>
            <button onClick={() => setTransmission(transmission === "manual" ? undefined : "manual")}>
              <Badge variant={transmission === "manual" ? "luxury" : "outline"}>
                Manual
              </Badge>
            </button>
          </div>
        </section>

        <section>
          <h3 className="text-sm font-bold uppercase tracking-[0.16em] text-slate-500">
            Features
          </h3>

          <div className="mt-3 flex flex-wrap gap-2">
            {features.map((feature) => (
              <button key={feature} onClick={() => toggleFeature(feature)}>
                <Badge variant={selectedFeatures.includes(feature) ? "luxury" : "outline"}>
                  {vehicleFeatureLabels[feature]}
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
                checked={Boolean(payAtPickup)}
                onChange={togglePayAtPickup}
                className="h-4 w-4 rounded border-slate-300 text-brand-600"
              />
              Pay at pickup
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
