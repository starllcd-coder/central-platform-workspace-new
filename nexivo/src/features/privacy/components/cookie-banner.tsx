"use client";

import { Cookie, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useConsentStore } from "@/features/privacy/store/consent.store";

export function CookieBanner() {
  const { hasHydrated, hasSavedConsent, acceptAll, rejectOptional } = useConsentStore();

  if (!hasHydrated || hasSavedConsent) return null;

  return (
    <div className="fixed bottom-5 left-1/2 z-[150] w-[calc(100%-2rem)] max-w-5xl -translate-x-1/2 rounded-4xl border border-slate-200 bg-white p-5 shadow-premium">
      <div className="grid gap-5 md:grid-cols-[auto_1fr_auto] md:items-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
          <Cookie size={22} />
        </div>

        <div>
          <h3 className="font-heading text-lg font-semibold text-luxury-ink">
            Nexivo uses cookies and consent preferences
          </h3>
          <p className="mt-1 text-sm leading-6 text-slate-600">
            Necessary cookies keep booking, login, language, currency, and security working.
            Optional cookies support analytics, personalization, and marketing.
          </p>
        </div>

        <div className="flex flex-wrap gap-2 md:justify-end">
          <Button asChild variant="outline">
            <a href="/cookie-center">
              <ShieldCheck className="mr-2" size={17} />
              Manage
            </a>
          </Button>
          <Button variant="outline" onClick={rejectOptional}>
            Reject Optional
          </Button>
          <Button variant="luxury" onClick={acceptAll}>
            Accept All
          </Button>
        </div>
      </div>
    </div>
  );
}
