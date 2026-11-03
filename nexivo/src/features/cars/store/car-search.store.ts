"use client";

import { create } from "zustand";
import type {
  CarSearchFilters,
  VehicleCategory,
  VehicleFeature
} from "@/features/cars/types/cars.types";

type CarSearchStore = CarSearchFilters & {
  setLocation: (location: string) => void;
  setDates: (pickupDate: string, returnDate: string) => void;
  toggleCategory: (category: VehicleCategory) => void;
  toggleFeature: (feature: VehicleFeature) => void;
  setTransmission: (transmission?: "automatic" | "manual") => void;
  toggleFreeCancellation: () => void;
  togglePayAtPickup: () => void;
  resetFilters: () => void;
};

const initialState: CarSearchFilters = {
  location: "",
  pickupDate: "",
  returnDate: "",
  category: [],
  features: [],
  minPrice: undefined,
  maxPrice: undefined,
  transmission: undefined,
  freeCancellation: undefined,
  payAtPickup: undefined
};

export const useCarSearchStore = create<CarSearchStore>((set) => ({
  ...initialState,

  setLocation: (location) => set({ location }),

  setDates: (pickupDate, returnDate) => set({ pickupDate, returnDate }),

  toggleCategory: (category) =>
    set((state) => ({
      category: state.category.includes(category)
        ? state.category.filter((item) => item !== category)
        : [...state.category, category]
    })),

  toggleFeature: (feature) =>
    set((state) => ({
      features: state.features.includes(feature)
        ? state.features.filter((item) => item !== feature)
        : [...state.features, feature]
    })),

  setTransmission: (transmission) => set({ transmission }),

  toggleFreeCancellation: () =>
    set((state) => ({
      freeCancellation: state.freeCancellation ? undefined : true
    })),

  togglePayAtPickup: () =>
    set((state) => ({
      payAtPickup: state.payAtPickup ? undefined : true
    })),

  resetFilters: () => set(initialState)
}));
