import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { CarSearchResults } from "@/features/cars/components/car-search-results";
import { createMetadata } from "@/lib/metadata";

export const metadata: Metadata = createMetadata({
  title: "Search Cars | Nexivo DriveSphere",
  description:
    "Search rental cars, SUVs, luxury vehicles, vans, and airport pickup options across GCC destinations through Nexivo DriveSphere.",
  path: "/cars/search"
});

export default function CarSearchPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="DriveSphere Search"
        title="Search rental vehicles across GCC destinations."
        description="Find verified vehicles with pickup options, payment choices, rental terms, insurance options, and DriveSphere-powered fleet availability."
      />

      <CarSearchResults />
    </PublicPageLayout>
  );
}
