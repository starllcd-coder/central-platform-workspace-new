import { notFound } from "next/navigation";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PropertyHero } from "@/features/stays/components/property-hero";
import { PropertyOverview } from "@/features/stays/components/property-overview";
import { RoomSelectionSection } from "@/features/stays/components/room-selection-section";
import { getCentralStayProperties } from "@/lib/marketplace/central-listings";

export default async function StayPropertyDetailsPage({
  params
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const property = (await getCentralStayProperties()).find((item) => item.slug === slug);

  if (!property) {
    notFound();
  }

  return (
    <PublicPageLayout>
      <PropertyHero property={property} />
      <PropertyOverview property={property} />
      <RoomSelectionSection property={property} />
    </PublicPageLayout>
  );
}
