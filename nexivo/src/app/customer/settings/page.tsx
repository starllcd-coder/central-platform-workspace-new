import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CurrencySelector } from "@/features/currency/components/currency-selector";
import { RegionSelector } from "@/features/geo/components/region-selector";
import { LanguageSelector } from "@/features/localization/components/language-selector";

export default function CustomerSettingsPage() {
  return (
    <div className="space-y-6">
      <Card variant="premium">
        <CardHeader>
          <CardTitle>Customer Preferences</CardTitle>
          <p className="text-sm leading-6 text-slate-600">
            Manage language, currency, country, city, timezone, and future privacy preferences.
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
