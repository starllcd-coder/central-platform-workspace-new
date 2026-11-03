"use client";

import { LaundryFilters } from "@/features/laundry/components/laundry-filters";
import { LaundryProviderCard } from "@/features/laundry/components/laundry-provider-card";
import { LaundrySearchBar } from "@/features/laundry/components/laundry-search-bar";
import { useLaundrySearchStore } from "@/features/laundry/store/laundry-search.store";
import { searchLaundryProviders } from "@/features/laundry/utils/laundry-search";
import { MarketplaceEmptyState } from "@/features/marketplace/components/marketplace-empty-state";
import type { LaundryProvider } from "@/features/laundry/types/laundry.types";

type LaundrySearchResultsProps = {
  providers?: LaundryProvider[];
};

export function LaundrySearchResults({ providers }: LaundrySearchResultsProps) {
  const filters = useLaundrySearchStore();
  const results = searchLaundryProviders(filters, providers);

  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <LaundrySearchBar />

        <div className="mt-8 grid gap-8 lg:grid-cols-[320px_1fr]">
          <LaundryFilters />

          <div>
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="font-heading text-2xl font-semibold text-luxury-ink">
                  {results.length} laundry providers found
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Powered by Laundrex service inventory and Nexivo marketplace search.
                </p>
              </div>

              <select className="h-11 rounded-full border border-slate-200 bg-white px-4 text-sm font-semibold shadow-soft">
                <option>Recommended</option>
                <option>Rating: high to low</option>
                <option>Minimum order: low to high</option>
                <option>Featured first</option>
              </select>
            </div>

            {results.length === 0 ? (
              <MarketplaceEmptyState
                title="No laundry providers matched your search"
                description="Try another city, area, service type, pickup option, or delivery option."
                actionHref="/laundry"
                actionLabel="Reset Laundry Search"
              />
            ) : (
              <div className="grid gap-6 xl:grid-cols-2">
                {results.map((provider) => (
                  <LaundryProviderCard key={provider.id} provider={provider} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
