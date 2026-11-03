"use client";

import { useEffect } from "react";
import { useLocalizationStore } from "@/features/localization/store/localization.store";

export function LocaleHtmlSync() {
  const { locale, direction } = useLocalizationStore();

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = direction;
  }, [locale, direction]);

  return null;
}
