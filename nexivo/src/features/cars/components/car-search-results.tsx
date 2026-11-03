"use client";

import { CarFilters } from "@/features/cars/components/car-filters";
import { CarSearchBar } from "@/features/cars/components/car-search-bar";
import { VehicleCard } from "@/features/cars/components/vehicle-card";
import { useCarSearchStore } from "@/features/cars/store/car-search.store";
import { searchRentalVehicles } from "@/features/cars/utils/car-search";
import { MarketplaceEmptyState } from "@/features/marketplace/components/marketplace-empty-state";
import type { RentalVehicle } from "@/features/cars/types/cars.types";

type CarSearchResultsProps = {
  vehicles?: RentalVehicle[];
};

export function CarSearchResults({ vehicles }: CarSearchResultsProps) {
  const filters = useCarSearchStore();
  const results = searchRentalVehicles(filters, vehicles);

  return (
    <section className="bg-luxury-mist pb-16 pt-4 md:pb-20 md:pt-6">
      <div className="nexivo-container">
        <CarSearchBar />

        <div className="mt-8 grid gap-8 lg:grid-cols-[320px_1fr]">
          <CarFilters />

          <div>
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="font-heading text-2xl font-semibold text-luxury-ink">
                  {results.length} cars found
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Powered by DriveSphere rental inventory and Nexivo marketplace search.
                </p>
              </div>

              <select className="h-11 rounded-full border border-slate-200 bg-white px-4 text-sm font-semibold shadow-soft">
                <option>Recommended</option>
                <option>Price: low to high</option>
                <option>Rating: high to low</option>
                <option>Featured first</option>
              </select>
            </div>

            {results.length === 0 ? (
              <MarketplaceEmptyState
                title="No cars matched your search"
                description="Try another city, pickup location, category, transmission, or payment option."
                actionHref="/cars"
                actionLabel="Reset Car Search"
              />
            ) : (
              <div className="grid gap-6 xl:grid-cols-2">
                {results.map((vehicle) => (
                  <VehicleCard key={vehicle.id} vehicle={vehicle} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
