import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";

export default function NotFound() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="404"
        title="Page not found."
        description="The page you are looking for does not exist or has moved."
        primaryLabel="Go Home"
        primaryHref="/"
        secondaryLabel="Explore Destinations"
        secondaryHref="/destinations"
      />
    </PublicPageLayout>
  );
}
