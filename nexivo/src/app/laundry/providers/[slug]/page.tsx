import { notFound } from "next/navigation";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { LaundryProviderHero } from "@/features/laundry/components/laundry-provider-hero";
import { LaundryProviderOverview } from "@/features/laundry/components/laundry-provider-overview";
import { LaundryServiceSelectionSection } from "@/features/laundry/components/laundry-service-selection-section";
import { getCentralLaundryProviders } from "@/lib/marketplace/central-listings";

export default async function LaundryProviderDetailsPage({
  params
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const provider = (await getCentralLaundryProviders()).find((item) => item.slug === slug);

  if (!provider) {
    notFound();
  }

  return (
    <PublicPageLayout>
      <LaundryProviderHero provider={provider} />
      <LaundryProviderOverview provider={provider} />
      <LaundryServiceSelectionSection provider={provider} />
    </PublicPageLayout>
  );
}
