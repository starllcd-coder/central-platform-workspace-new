"use client";

import { LanguageSelector } from "@/features/localization/components/language-selector";

export function LanguageSettingsPanel() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container max-w-4xl">
        <LanguageSelector />
      </div>
    </section>
  );
}
