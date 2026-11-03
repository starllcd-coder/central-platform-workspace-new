import type { Metadata } from "next";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { LaundrySearchResults } from "@/features/laundry/components/laundry-search-results";
import { createMetadata } from "@/lib/metadata";

export const metadata: Metadata = createMetadata({
  title: "Order Laundry | Nexivo Laundrex",
  description:
    "Start a laundry pickup and delivery order through Nexivo Laundrex.",
  path: "/laundry/order"
});

export default function LaundryOrderPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Laundrex Order"
        title="Start your laundry order."
        description="Choose a provider, select services, schedule pickup, add customer details, and continue to payment or pay-on-delivery."
      />

      <LaundrySearchResults />
    </PublicPageLayout>
  );
}
