import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CurrencySelector } from "@/features/currency/components/currency-selector";
import { RegionSelector } from "@/features/geo/components/region-selector";
import { LanguageSelector } from "@/features/localization/components/language-selector";

export default function PartnerSettingsPage() {
  return (
    <div className="space-y-6">
      <Card variant="premium">
        <CardHeader>
          <CardTitle>Partner Settings</CardTitle>
          <p className="text-sm leading-6 text-slate-600">
            Configure regional settings, language, currency, business preferences, and future DSS Central Platform sync.
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          <RegionSelector />
          <CurrencySelector />
          <LanguageSelector />
        </CardContent>
      </Card>
    </div>
  );
}
