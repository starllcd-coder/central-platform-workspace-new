import type { Metadata } from "next";
import { baseSeo, type SeoConfig } from "@/config/seo";

export function createMetadata(config: SeoConfig): Metadata {
  const url = config.path ? `${baseSeo.baseUrl}${config.path}` : baseSeo.baseUrl;

  return {
    title: config.title,
    description: config.description,
    keywords: [...baseSeo.defaultKeywords, ...(config.keywords ?? [])],
    alternates: {
      canonical: url
    },
    robots: {
      index: !config.noIndex,
      follow: !config.noIndex
    },
    openGraph: {
      title: config.title,
      description: config.description,
      url,
      siteName: baseSeo.siteName,
      type: "website"
    },
    twitter: {
      card: "summary_large_image",
      title: config.title,
      description: config.description
    }
  };
}
