import { Car, Hotel, Shirt } from "lucide-react";

export type BookingServiceType = "stays" | "cars" | "laundry";

export const bookingServiceTabs = [
  {
    value: "stays",
    label: "Stays",
    description: "Hotels, apartments, villas, and serviced residences.",
    icon: Hotel,
    accent: "bg-brand-50 text-brand-700"
  },
  {
    value: "cars",
    label: "Cars",
    description: "Airport, city, SUV, economy, luxury, and business rentals.",
    icon: Car,
    accent: "bg-luxury-ink text-white"
  },
  {
    value: "laundry",
    label: "Laundry",
    description: "Pickup, delivery, wash, press, and hotel guest laundry.",
    icon: Shirt,
    accent: "bg-luxury-gold/15 text-luxury-bronze"
  }
] as const;
