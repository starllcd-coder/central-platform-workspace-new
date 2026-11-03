import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { LaundrySearchResults } from "@/features/laundry/components/laundry-search-results";
import { createMetadata } from "@/lib/metadata";

export const metadata: Metadata = createMetadata({
  title: "Laundry Providers | Nexivo Laundrex",
  description:
    "Search laundry pickup and delivery providers across GCC destinations through Nexivo Laundrex.",
  path: "/laundry/providers"
});

export default function LaundryProvidersPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Laundry Providers"
        title="Search laundry providers across GCC cities."
        description="Find pickup, delivery, wash, iron, dry cleaning, express, and hotel guest laundry services."
      />

      <LaundrySearchResults />
    </PublicPageLayout>
  );
}
