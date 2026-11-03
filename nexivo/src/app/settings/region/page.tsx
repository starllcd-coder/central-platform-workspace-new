import { CurrencySelector } from "@/features/currency/components/currency-selector";
import { RegionSelector } from "@/features/geo/components/region-selector";
import { LanguageSettingsPanel } from "@/components/localization/language-settings-panel";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";

export default function RegionSettingsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Region Settings"
        title="Configure country, city, language, currency, and timezone."
        description="Nexivo is prepared for GCC launch and future European expansion with customer preference controls and business settlement separation."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container space-y-8">
          <RegionSelector />
          <CurrencySelector />
        </div>
      </section>

      <LanguageSettingsPanel />
    </PublicPageLayout>
  );
}
