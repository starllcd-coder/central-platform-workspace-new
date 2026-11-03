export type SeoConfig = {
  title: string;
  description: string;
  path?: string;
  keywords?: string[];
  noIndex?: boolean;
};

export const baseSeo = {
  siteName: "Nexivo",
  companyName: "Deedarian Software Solutions",
  baseUrl: "https://nexivo.com",
  defaultDescription:
    "Nexivo is a GCC-first, Europe-ready marketplace for stays, car rentals, and laundry services powered by DSS.",
  defaultKeywords: [
    "Nexivo",
    "DSS",
    "Deedarian Software Solutions",
    "StayLux",
    "DriveSphere",
    "Laundrex",
    "GCC hotel booking",
    "GCC car rental",
    "laundry services GCC"
  ]
} as const;

export const pageSeo = {
  home: {
    title: "Nexivo | Stays, Cars & Laundry in One Platform",
    description:
      "Book your stay, rent your car, and manage laundry services across the GCC through one premium Nexivo account."
  },
  stays: {
    title: "Stays | Hotels, Apartments & Villas",
    description:
      "Search hotels, apartments, villas, and serviced residences across GCC destinations through Nexivo StayLux."
  },
  cars: {
    title: "Cars | Car Rental Marketplace",
    description:
      "Find and book rental cars across GCC cities with DriveSphere-powered vehicle search and booking."
  },
  laundry: {
    title: "Laundry | Pickup & Delivery Services",
    description:
      "Schedule laundry pickup and delivery services during your stay or daily life through Nexivo Laundrex."
  },
  destinations: {
    title: "Destinations | GCC City Guides",
    description:
      "Explore GCC destinations, travel guides, city pages, local attractions, stays, cars, and services."
  },
  business: {
    title: "For Business | Join Nexivo",
    description:
      "Hotels, car rental companies, and laundry businesses can join Nexivo and use DSS-powered platforms."
  },
  pricing: {
    title: "Pricing | Nexivo Business Plans",
    description:
      "View Nexivo setup fee structure, commission-based models for StayLux and DriveSphere, and Laundrex subscriptions."
  },
  about: {
    title: "About DSS | Deedarian Software Solutions",
    description:
      "Learn about Deedarian Software Solutions, the company powering Nexivo, StayLux, DriveSphere, and Laundrex."
  },
  contact: {
    title: "Contact | Nexivo",
    description:
      "Contact Nexivo and Deedarian Software Solutions for bookings, partnerships, demos, and platform support."
  }
} as const;
