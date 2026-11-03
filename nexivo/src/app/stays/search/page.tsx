import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { StaySearchResults } from "@/features/stays/components/stay-search-results";
import { createMetadata } from "@/lib/metadata";

export const metadata: Metadata = createMetadata({
  title: "Search Stays | Nexivo StayLux",
  description:
    "Search hotels, apartments, villas, and serviced residences across GCC destinations through Nexivo StayLux.",
  path: "/stays/search"
});

export default function StaySearchPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="StayLux Search"
        title="Search hotels, apartments, villas, and serviced residences."
        description="Find verified accommodation listings across GCC destinations with pay-at-property options, free cancellation, and premium marketplace discovery."
      />

      <StaySearchResults />
    </PublicPageLayout>
  );
}
