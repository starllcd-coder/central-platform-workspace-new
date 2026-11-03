import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { LanguageSettingsPanel } from "@/components/localization/language-settings-panel";

export default function LanguagePage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Language Preferences"
        title="Choose your Nexivo language."
        description="Nexivo launches with English and Arabic, while German, French, Spanish, Italian, Portuguese, Dutch, Turkish, and Russian are prepared for European expansion."
      />

      <LanguageSettingsPanel />
    </PublicPageLayout>
  );
}
