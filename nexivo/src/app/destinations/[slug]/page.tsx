import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { DestinationCrossSellSection } from "@/features/destinations/components/destination-cross-sell-section";
import { DestinationExperiencesSection } from "@/features/destinations/components/destination-experiences-section";
import { DestinationHero } from "@/features/destinations/components/destination-hero";
import { DestinationTravelTips } from "@/features/destinations/components/destination-travel-tips";
import {
  getDestinationExperiences,
  getDestinationGuideBySlug
} from "@/features/destinations/utils/destination-utils";
import { createMetadata } from "@/lib/metadata";

export async function generateMetadata({
  params
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const destination = getDestinationGuideBySlug(slug);

  if (!destination) {
    return createMetadata({
      title: "Destination Not Found | Nexivo",
      description: "This Nexivo destination page was not found.",
      path: `/destinations/${slug}`,
      noIndex: true
    });
  }

  return createMetadata({
    title: `${destination.city} Travel Guide | Nexivo`,
    description: destination.description,
    path: `/destinations/${destination.slug}`,
    keywords: destination.seoKeywords
  });
}

export default async function DestinationDetailsPage({
  params
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const destination = getDestinationGuideBySlug(slug);

  if (!destination) {
    notFound();
  }

  const experiences = getDestinationExperiences(destination.slug);

  return (
    <PublicPageLayout>
      <DestinationHero destination={destination} />
      <DestinationCrossSellSection destination={destination} />
      <DestinationExperiencesSection experiences={experiences} />
      <DestinationTravelTips destination={destination} />
    </PublicPageLayout>
  );
}