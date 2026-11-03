export type DestinationGuide = {
  slug: string;
  city: string;
  country: string;
  countryCode: string;
  headline: string;
  description: string;
  heroImage: string;
  bestFor: string[];
  travelTips: string[];
  seoKeywords: string[];
  staySearchPath: string;
  carSearchPath: string;
  laundrySearchPath: string;
};

export type DestinationExperience = {
  id: string;
  destinationSlug: string;
  title: string;
  description: string;
  category: "nature" | "shopping" | "business" | "culture" | "family" | "airport" | "seasonal";
};
