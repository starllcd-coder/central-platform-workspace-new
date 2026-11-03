import type { City } from "@/features/geo/types/geo.types";

export const gccCities: City[] = [
  {
    id: "om-muscat",
    name: "Muscat",
    countryCode: "OM",
    slug: "muscat",
    airportCodes: ["MCT"],
    isTouristDestination: true,
    priority: 100
  },
  {
    id: "om-salalah",
    name: "Salalah",
    countryCode: "OM",
    slug: "salalah",
    airportCodes: ["SLL"],
    isTouristDestination: true,
    priority: 100
  },
  {
    id: "om-nizwa",
    name: "Nizwa",
    countryCode: "OM",
    slug: "nizwa",
    isTouristDestination: true,
    priority: 80
  },
  {
    id: "om-sohar",
    name: "Sohar",
    countryCode: "OM",
    slug: "sohar",
    isTouristDestination: false,
    priority: 65
  },
  {
    id: "om-sur",
    name: "Sur",
    countryCode: "OM",
    slug: "sur",
    isTouristDestination: true,
    priority: 70
  },
  {
    id: "om-duqm",
    name: "Duqm",
    countryCode: "OM",
    slug: "duqm",
    isTouristDestination: false,
    priority: 60
  },
  {
    id: "om-khasab",
    name: "Khasab",
    countryCode: "OM",
    slug: "khasab",
    isTouristDestination: true,
    priority: 72
  },
  {
    id: "ae-dubai",
    name: "Dubai",
    countryCode: "AE",
    slug: "dubai",
    airportCodes: ["DXB", "DWC"],
    isTouristDestination: true,
    priority: 100
  },
  {
    id: "ae-abu-dhabi",
    name: "Abu Dhabi",
    countryCode: "AE",
    slug: "abu-dhabi",
    airportCodes: ["AUH"],
    isTouristDestination: true,
    priority: 95
  },
  {
    id: "ae-sharjah",
    name: "Sharjah",
    countryCode: "AE",
    slug: "sharjah",
    airportCodes: ["SHJ"],
    isTouristDestination: true,
    priority: 85
  },
  {
    id: "ae-ajman",
    name: "Ajman",
    countryCode: "AE",
    slug: "ajman",
    isTouristDestination: true,
    priority: 70
  },
  {
    id: "ae-ras-al-khaimah",
    name: "Ras Al Khaimah",
    countryCode: "AE",
    slug: "ras-al-khaimah",
    airportCodes: ["RKT"],
    isTouristDestination: true,
    priority: 82
  },
  {
    id: "ae-fujairah",
    name: "Fujairah",
    countryCode: "AE",
    slug: "fujairah",
    isTouristDestination: true,
    priority: 76
  },
  {
    id: "sa-riyadh",
    name: "Riyadh",
    countryCode: "SA",
    slug: "riyadh",
    airportCodes: ["RUH"],
    isTouristDestination: true,
    priority: 95
  },
  {
    id: "sa-jeddah",
    name: "Jeddah",
    countryCode: "SA",
    slug: "jeddah",
    airportCodes: ["JED"],
    isTouristDestination: true,
    priority: 95
  },
  {
    id: "sa-makkah",
    name: "Makkah",
    countryCode: "SA",
    slug: "makkah",
    isTouristDestination: true,
    priority: 90
  },
  {
    id: "sa-madinah",
    name: "Madinah",
    countryCode: "SA",
    slug: "madinah",
    airportCodes: ["MED"],
    isTouristDestination: true,
    priority: 90
  },
  {
    id: "sa-dammam",
    name: "Dammam",
    countryCode: "SA",
    slug: "dammam",
    airportCodes: ["DMM"],
    isTouristDestination: false,
    priority: 75
  },
  {
    id: "sa-khobar",
    name: "Khobar",
    countryCode: "SA",
    slug: "khobar",
    isTouristDestination: true,
    priority: 72
  },
  {
    id: "sa-alula",
    name: "AlUla",
    countryCode: "SA",
    slug: "alula",
    airportCodes: ["ULH"],
    isTouristDestination: true,
    priority: 88
  },
  {
    id: "qa-doha",
    name: "Doha",
    countryCode: "QA",
    slug: "doha",
    airportCodes: ["DOH"],
    isTouristDestination: true,
    priority: 95
  },
  {
    id: "qa-lusail",
    name: "Lusail",
    countryCode: "QA",
    slug: "lusail",
    isTouristDestination: true,
    priority: 78
  },
  {
    id: "qa-al-wakrah",
    name: "Al Wakrah",
    countryCode: "QA",
    slug: "al-wakrah",
    isTouristDestination: true,
    priority: 72
  },
  {
    id: "bh-manama",
    name: "Manama",
    countryCode: "BH",
    slug: "manama",
    airportCodes: ["BAH"],
    isTouristDestination: true,
    priority: 90
  },
  {
    id: "bh-muharraq",
    name: "Muharraq",
    countryCode: "BH",
    slug: "muharraq",
    isTouristDestination: true,
    priority: 74
  },
  {
    id: "kw-kuwait-city",
    name: "Kuwait City",
    countryCode: "KW",
    slug: "kuwait-city",
    airportCodes: ["KWI"],
    isTouristDestination: true,
    priority: 90
  },
  {
    id: "kw-salmiya",
    name: "Salmiya",
    countryCode: "KW",
    slug: "salmiya",
    isTouristDestination: true,
    priority: 72
  },
  {
    id: "kw-hawalli",
    name: "Hawalli",
    countryCode: "KW",
    slug: "hawalli",
    isTouristDestination: false,
    priority: 65
  }
];

export const allCities = [...gccCities];
