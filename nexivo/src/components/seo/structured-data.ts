export const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "Deedarian Software Solutions",
  alternateName: "DSS",
  brand: {
    "@type": "Brand",
    name: "Nexivo"
  },
  url: "https://nexivo.com",
  description:
    "Deedarian Software Solutions powers Nexivo, StayLux, DriveSphere, Laundrex, and DSS Central Platform."
};

export const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "Nexivo",
  url: "https://nexivo.com",
  potentialAction: {
    "@type": "SearchAction",
    target: "https://nexivo.com/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
};
