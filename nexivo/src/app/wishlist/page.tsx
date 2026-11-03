import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { WishlistGrid } from "@/features/engagement/components/wishlist-grid";

export default function WishlistPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Wishlist"
        title="Save hotels, cars, laundry providers, and future destinations."
        description="Nexivo wishlist helps customers return to saved options and complete bookings later."
      />

      <WishlistGrid />
    </PublicPageLayout>
  );
}
