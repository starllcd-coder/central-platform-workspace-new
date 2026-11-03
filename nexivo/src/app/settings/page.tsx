import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { RegionSelector } from "@/features/geo/components/region-selector";
import { CurrencySelector } from "@/features/currency/components/currency-selector";

export default function SettingsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Settings"
        title="Manage your Nexivo regional preferences."
        description="Language, currency, country, city, timezone, and future privacy preferences can be managed here."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container space-y-8">
          <RegionSelector />
          <CurrencySelector />
        </div>
      </section>
    </PublicPageLayout>
  );
}
