"use client";

import { StayFilters } from "@/features/stays/components/stay-filters";
import { StayPropertyCard } from "@/features/stays/components/stay-property-card";
import { StaySearchBar } from "@/features/stays/components/stay-search-bar";
import { useStaySearchStore } from "@/features/stays/store/stay-search.store";
import { searchStayProperties } from "@/features/stays/utils/stay-search";
import { MarketplaceEmptyState } from "@/features/marketplace/components/marketplace-empty-state";
import type { StayProperty } from "@/features/stays/types/stays.types";

type StaySearchResultsProps = {
  properties?: StayProperty[];
};

export function StaySearchResults({ properties }: StaySearchResultsProps) {
  const filters = useStaySearchStore();
  const results = searchStayProperties(filters, properties);

  return (
    <section className="bg-luxury-mist pb-16 pt-8 md:pb-20 md:pt-10">
      <div className="nexivo-container">
        <StaySearchBar />

        <div className="mt-8 grid gap-8 lg:grid-cols-[320px_1fr]">
          <StayFilters />

          <div>
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="font-heading text-2xl font-semibold text-luxury-ink">
                  {results.length} stays found
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Powered by StayLux inventory and Nexivo destination search.
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
                title="No stays matched your search"
                description="Try another destination, property type, amenity, or cancellation option."
                actionHref="/destinations"
                actionLabel="Explore GCC Destinations"
              />
            ) : (
              <div className="grid gap-6 xl:grid-cols-2">
                {results.map((property) => (
                  <StayPropertyCard key={property.id} property={property} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
