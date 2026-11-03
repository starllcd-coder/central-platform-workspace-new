import type {
  DestinationExperience,
  DestinationGuide
} from "@/features/destinations/types/destination.types";

export const destinationGuides: DestinationGuide[] = [
  {
    slug: "salalah",
    city: "Salalah",
    country: "Oman",
    countryCode: "OM",
    headline: "Plan your Salalah stay, car rental, and laundry services in one Nexivo journey.",
    description:
      "Salalah is one of Oman's strongest tourism destinations, especially during Khareef season. Nexivo brings together StayLux accommodation, DriveSphere car rental, and Laundrex laundry services for families, tourists, and residents.",
    heroImage: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1600&auto=format&fit=crop",
    bestFor: ["Khareef Season", "Family Travel", "Nature", "Apartments", "Airport Car Rental"],
    travelTips: [
      "Book accommodation early during Khareef season.",
      "A rental car is useful for waterfalls, beaches, and mountain viewpoints.",
      "Laundry pickup is useful for families staying several days.",
      "Keep card guarantee ready for stays and car rental bookings."
    ],
    seoKeywords: [
      "Salalah hotel booking",
      "Salalah apartment booking",
      "Salalah car rental",
      "Salalah laundry pickup",
      "Khareef Salalah stays"
    ],
    staySearchPath: "/stays?destination=salalah",
    carSearchPath: "/cars?location=salalah",
    laundrySearchPath: "/laundry?location=salalah"
  },
  {
    slug: "muscat",
    city: "Muscat",
    country: "Oman",
    countryCode: "OM",
    headline: "Book Muscat hotels, rental cars, and city services with Nexivo.",
    description:
      "Muscat is ideal for business, culture, beaches, shopping, and airport-connected travel. Nexivo helps customers combine accommodation, mobility, and laundry services in one account.",
    heroImage: "https://images.unsplash.com/photo-1578894381163-e72c17f2d45f?q=80&w=1600&auto=format&fit=crop",
    bestFor: ["Business Travel", "Culture", "Beaches", "Airport Pickup", "Premium Hotels"],
    travelTips: [
      "Choose Qurum, Mutrah, or airport areas based on your travel purpose.",
      "Airport car pickup is convenient for short business trips.",
      "Hotels and serviced apartments should clearly show cancellation and payment rules.",
      "Laundry pickup is helpful for long-stay apartment guests."
    ],
    seoKeywords: [
      "Muscat hotel booking",
      "Muscat car rental",
      "Muscat serviced apartments",
      "Muscat laundry delivery"
    ],
    staySearchPath: "/stays?destination=muscat",
    carSearchPath: "/cars?location=muscat",
    laundrySearchPath: "/laundry?location=muscat"
  },
  {
    slug: "dubai",
    city: "Dubai",
    country: "United Arab Emirates",
    countryCode: "AE",
    headline: "Discover Dubai stays, cars, and travel services with Nexivo.",
    description:
      "Dubai is a global tourism, shopping, business, and luxury destination. Nexivo is prepared to support hotels, apartments, car rental, and laundry services across high-demand areas.",
    heroImage: "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=1600&auto=format&fit=crop",
    bestFor: ["Luxury Travel", "Shopping", "Business", "Apartments", "Airport Mobility"],
    travelTips: [
      "Compare hotel and apartment options by area such as Marina, Downtown, and Deira.",
      "Car rental rules may require deposit and card guarantee.",
      "Laundry pickup is useful for apartment stays and business travelers.",
      "Keep payment and cancellation policies clear before booking."
    ],
    seoKeywords: [
      "Dubai hotel booking",
      "Dubai apartment rental",
      "Dubai car rental",
      "Dubai laundry pickup"
    ],
    staySearchPath: "/stays?destination=dubai",
    carSearchPath: "/cars?location=dubai",
    laundrySearchPath: "/laundry?location=dubai"
  },
  {
    slug: "doha",
    city: "Doha",
    country: "Qatar",
    countryCode: "QA",
    headline: "Book Doha stays, car rentals, and laundry pickup services.",
    description:
      "Doha is a premium business, family, and events destination. Nexivo supports a connected journey from hotel booking to car rental and laundry services.",
    heroImage: "https://images.unsplash.com/photo-1590579491624-f98f36d4c763?q=80&w=1600&auto=format&fit=crop",
    bestFor: ["Business", "Events", "Family Travel", "Premium Hotels", "Airport Pickup"],
    travelTips: [
      "West Bay is useful for business and premium hotel stays.",
      "Airport pickup can simplify short business trips.",
      "Laundry services are useful for hotel guests and serviced apartment stays.",
      "Check deposit and card guarantee rules for rental cars."
    ],
    seoKeywords: [
      "Doha hotel booking",
      "Doha car rental",
      "Doha laundry pickup",
      "West Bay hotel booking"
    ],
    staySearchPath: "/stays?destination=doha",
    carSearchPath: "/cars?location=doha",
    laundrySearchPath: "/laundry?location=doha"
  },
  {
    slug: "riyadh",
    city: "Riyadh",
    country: "Saudi Arabia",
    countryCode: "SA",
    headline: "Manage Riyadh business travel with stays, cars, and services.",
    description:
      "Riyadh is a major business, government, events, and mobility destination. Nexivo supports accommodation, car rental, and service discovery for corporate and leisure travelers.",
    heroImage: "https://images.unsplash.com/photo-1586724237569-f3d0c1dee8c6?q=80&w=1600&auto=format&fit=crop",
    bestFor: ["Corporate Travel", "Events", "Serviced Apartments", "Airport Rental", "Long Stays"],
    travelTips: [
      "Business travelers should compare serviced apartments and hotels by district.",
      "Car rental can be useful for airport, meetings, and city movement.",
      "Document and license details should be ready for rental booking.",
      "Use loyalty and business travel promotions when available."
    ],
    seoKeywords: [
      "Riyadh hotel booking",
      "Riyadh serviced apartments",
      "Riyadh car rental",
      "Riyadh laundry service"
    ],
    staySearchPath: "/stays?destination=riyadh",
    carSearchPath: "/cars?location=riyadh",
    laundrySearchPath: "/laundry?location=riyadh"
  },
  {
    slug: "kuwait-city",
    city: "Kuwait City",
    country: "Kuwait",
    countryCode: "KW",
    headline: "Search Kuwait City stays, cars, and local services.",
    description:
      "Kuwait City is a business, shopping, and city travel destination. Nexivo connects accommodation, car rentals, and service providers in one customer experience.",
    heroImage: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1600&auto=format&fit=crop",
    bestFor: ["Business", "Shopping", "City Hotels", "Airport Transfer", "Family Travel"],
    travelTips: [
      "Choose city areas based on business meetings or shopping plans.",
      "Car rental providers should show deposit, mileage, and insurance terms clearly.",
      "Laundry pickup helps longer apartment stays.",
      "Use the same Nexivo account for booking history and preferences."
    ],
    seoKeywords: [
      "Kuwait City hotel booking",
      "Kuwait City car rental",
      "Kuwait City laundry pickup"
    ],
    staySearchPath: "/stays?destination=kuwait-city",
    carSearchPath: "/cars?location=kuwait-city",
    laundrySearchPath: "/laundry?location=kuwait-city"
  }
];

export const destinationExperiences: DestinationExperience[] = [
  {
    id: "exp-salalah-1",
    destinationSlug: "salalah",
    title: "Khareef family travel",
    description: "Seasonal stays, rental cars, and laundry support for families visiting Salalah.",
    category: "seasonal"
  },
  {
    id: "exp-salalah-2",
    destinationSlug: "salalah",
    title: "Nature and mountain routes",
    description: "Car rental helps tourists reach waterfalls, beaches, and mountain viewpoints.",
    category: "nature"
  },
  {
    id: "exp-muscat-1",
    destinationSlug: "muscat",
    title: "Culture and waterfront stays",
    description: "Stay near Mutrah, Qurum, and beaches with mobility and city services.",
    category: "culture"
  },
  {
    id: "exp-dubai-1",
    destinationSlug: "dubai",
    title: "Luxury apartment and car rental journey",
    description: "Combine premium apartment stays with rental cars and laundry pickup.",
    category: "shopping"
  },
  {
    id: "exp-doha-1",
    destinationSlug: "doha",
    title: "Business travel in West Bay",
    description: "Premium hotels, executive car rentals, and laundry support for professionals.",
    category: "business"
  },
  {
    id: "exp-riyadh-1",
    destinationSlug: "riyadh",
    title: "Corporate long-stay support",
    description: "Serviced apartments, rental vehicles, and laundry services for extended stays.",
    category: "business"
  }
];
