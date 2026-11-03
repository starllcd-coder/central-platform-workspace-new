"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { laundryFeatureLabels, laundryServiceTypeLabels } from "@/features/laundry/data/laundry-labels";
import { useLaundrySearchStore } from "@/features/laundry/store/laundry-search.store";
import type { LaundryProviderFeature, LaundryServiceType } from "@/features/laundry/types/laundry.types";

const serviceTypes = Object.keys(laundryServiceTypeLabels) as LaundryServiceType[];
const features = Object.keys(laundryFeatureLabels) as LaundryProviderFeature[];

export function LaundryFilters() {
  const {
    serviceTypes: selectedServiceTypes,
    features: selectedFeatures,
    pickupAvailable,
    deliveryAvailable,
    toggleServiceType,
    toggleFeature,
    togglePickupAvailable,
    toggleDeliveryAvailable,
    resetFilters
  } = useLaundrySearchStore();

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
            Services
          </h3>

          <div className="mt-3 flex flex-wrap gap-2">
            {serviceTypes.map((item) => (
              <button key={item} onClick={() => toggleServiceType(item)}>
                <Badge variant={selectedServiceTypes.includes(item) ? "luxury" : "outline"}>
                  {laundryServiceTypeLabels[item]}
                </Badge>
              </button>
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-sm font-bold uppercase tracking-[0.16em] text-slate-500">
            Features
          </h3>

          <div className="mt-3 flex flex-wrap gap-2">
            {features.map((item) => (
              <button key={item} onClick={() => toggleFeature(item)}>
                <Badge variant={selectedFeatures.includes(item) ? "luxury" : "outline"}>
                  {laundryFeatureLabels[item]}
                </Badge>
              </button>
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-sm font-bold uppercase tracking-[0.16em] text-slate-500">
            Options
          </h3>

          <div className="mt-3 space-y-3">
            <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
              <input
                type="checkbox"
                checked={Boolean(pickupAvailable)}
                onChange={togglePickupAvailable}
                className="h-4 w-4 rounded border-slate-300 text-brand-600"
              />
              Pickup available
            </label>

            <label className="flex items-center gap-3 text-sm font-medium text-slate-700">
              <input
                type="checkbox"
                checked={Boolean(deliveryAvailable)}
                onChange={toggleDeliveryAvailable}
                className="h-4 w-4 rounded border-slate-300 text-brand-600"
              />
              Delivery available
            </label>
          </div>
        </section>
      </div>
    </aside>
  );
}
