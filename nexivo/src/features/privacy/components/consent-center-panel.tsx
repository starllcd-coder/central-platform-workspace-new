"use client";

import { Cookie } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useConsentStore } from "@/features/privacy/store/consent.store";

export function ConsentCenterPanel() {
  const {
    preferences,
    toggleConsent,
    acceptAll,
    rejectOptional,
    saveConsent,
    resetConsent
  } = useConsentStore();

  return (
    <Card variant="premium">
      <CardHeader>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <CardTitle>Cookie & Consent Center</CardTitle>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Manage consent for necessary, analytics, marketing, personalization, and third-party
              integrations. This is prepared for GCC launch and future GDPR requirements.
            </p>
          </div>

          <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
            <Cookie size={22} />
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {preferences.map((preference) => (
          <div
            key={preference.category}
            className="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-5 shadow-soft md:flex-row md:items-center md:justify-between"
          >
            <div>
              <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                {preference.title}
              </h3>
              <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-600">
                {preference.description}
              </p>
              {preference.required ? (
                <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-brand-700">
                  Always required
                </p>
              ) : null}
            </div>

            <label className="relative inline-flex cursor-pointer items-center">
              <input
                type="checkbox"
                checked={preference.enabled}
                disabled={preference.required}
                onChange={() => toggleConsent(preference.category)}
                className="peer sr-only"
              />
              <span className="h-7 w-12 rounded-full bg-slate-200 after:absolute after:left-1 after:top-1 after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all peer-checked:bg-brand-600 peer-checked:after:translate-x-5 peer-disabled:opacity-60" />
            </label>
          </div>
        ))}

        <div className="flex flex-wrap justify-end gap-3 pt-4">
          <Button variant="outline" onClick={resetConsent}>
            Reset
          </Button>
          <Button variant="outline" onClick={rejectOptional}>
            Reject Optional
          </Button>
          <Button variant="gold" onClick={acceptAll}>
            Accept All
          </Button>
          <Button variant="luxury" onClick={saveConsent}>
            Save Preferences
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
