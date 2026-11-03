export type CountryCode =
  | "OM"
  | "AE"
  | "SA"
  | "QA"
  | "BH"
  | "KW"
  | "DE"
  | "FR"
  | "ES"
  | "IT"
  | "PT"
  | "NL"
  | "TR"
  | "RU"
  | "GB"
  | "US";

export type RegionGroup = "GCC" | "Europe" | "International";

export type Country = {
  code: CountryCode;
  name: string;
  nativeName?: string;
  currency: string;
  phoneCode: string;
  timezone: string;
  regionGroup: RegionGroup;
  launchCountry: boolean;
};

export type City = {
  id: string;
  name: string;
  countryCode: CountryCode;
  slug: string;
  airportCodes?: string[];
  isTouristDestination: boolean;
  priority: number;
};

export type Destination = {
  id: string;
  cityId: string;
  name: string;
  slug: string;
  type: "city" | "area" | "airport" | "tourist-zone";
  description: string;
};
