import { notFound } from "next/navigation";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { LaundryOrderCheckout } from "@/features/laundry/components/laundry-order-checkout";
import { getCentralLaundryProviders } from "@/lib/marketplace/central-listings";

export default async function LaundryProviderOrderPage({
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
      <PageHero
        eyebrow="Laundrex Order"
        title="Complete your laundry order."
        description="Select pickup details, customer information, service quantity, delivery preference, and payment option."
      />

      <LaundryOrderCheckout provider={provider} />
    </PublicPageLayout>
  );
}
