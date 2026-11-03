import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";

export default function CookiesPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Cookie Policy"
        title="Cookie and consent controls."
        description="Nexivo will support cookie preferences, analytics consent, marketing consent, and Europe-ready compliance controls."
      />
    </PublicPageLayout>
  );
}
