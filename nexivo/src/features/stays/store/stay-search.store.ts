"use client";

import { create } from "zustand";
import type {
  PropertyAmenity,
  PropertyType,
  StaySearchFilters
} from "@/features/stays/types/stays.types";

type StaySearchStore = StaySearchFilters & {
  setDestination: (destination: string) => void;
  setDates: (checkIn: string, checkOut: string) => void;
  setGuests: (guests: number) => void;
  togglePropertyType: (type: PropertyType) => void;
  toggleAmenity: (amenity: PropertyAmenity) => void;
  setRating: (rating?: number) => void;
  togglePayAtProperty: () => void;
  toggleFreeCancellation: () => void;
  resetFilters: () => void;
};

const initialState: StaySearchFilters = {
  destination: "",
  checkIn: "",
  checkOut: "",
  guests: 2,
  propertyTypes: [],
  amenities: [],
  minPrice: undefined,
  maxPrice: undefined,
  rating: undefined,
  payAtProperty: undefined,
  freeCancellation: undefined
};

export const useStaySearchStore = create<StaySearchStore>((set) => ({
  ...initialState,

  setDestination: (destination) => set({ destination }),

  setDates: (checkIn, checkOut) => set({ checkIn, checkOut }),

  setGuests: (guests) => set({ guests }),

  togglePropertyType: (type) =>
    set((state) => ({
      propertyTypes: state.propertyTypes.includes(type)
        ? state.propertyTypes.filter((item) => item !== type)
        : [...state.propertyTypes, type]
    })),

  toggleAmenity: (amenity) =>
    set((state) => ({
      amenities: state.amenities.includes(amenity)
        ? state.amenities.filter((item) => item !== amenity)
        : [...state.amenities, amenity]
    })),

  setRating: (rating) => set({ rating }),

  togglePayAtProperty: () =>
    set((state) => ({
      payAtProperty: state.payAtProperty ? undefined : true
    })),

  toggleFreeCancellation: () =>
    set((state) => ({
      freeCancellation: state.freeCancellation ? undefined : true
    })),

  resetFilters: () => set(initialState)
}));
