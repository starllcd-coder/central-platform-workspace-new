"use client";

import { create } from "zustand";
import type {
  LaundryProviderFeature,
  LaundrySearchFilters,
  LaundryServiceType
} from "@/features/laundry/types/laundry.types";

type LaundrySearchStore = LaundrySearchFilters & {
  setLocation: (location: string) => void;
  setPickupDate: (pickupDate: string) => void;
  toggleServiceType: (serviceType: LaundryServiceType) => void;
  toggleFeature: (feature: LaundryProviderFeature) => void;
  togglePickupAvailable: () => void;
  toggleDeliveryAvailable: () => void;
  resetFilters: () => void;
};

const initialState: LaundrySearchFilters = {
  location: "",
  serviceTypes: [],
  features: [],
  pickupDate: "",
  pickupAvailable: undefined,
  deliveryAvailable: undefined
};

export const useLaundrySearchStore = create<LaundrySearchStore>((set) => ({
  ...initialState,

  setLocation: (location) => set({ location }),

  setPickupDate: (pickupDate) => set({ pickupDate }),

  toggleServiceType: (serviceType) =>
    set((state) => ({
      serviceTypes: state.serviceTypes.includes(serviceType)
        ? state.serviceTypes.filter((item) => item !== serviceType)
        : [...state.serviceTypes, serviceType]
    })),

  toggleFeature: (feature) =>
    set((state) => ({
      features: state.features.includes(feature)
        ? state.features.filter((item) => item !== feature)
        : [...state.features, feature]
    })),

  togglePickupAvailable: () =>
    set((state) => ({
      pickupAvailable: state.pickupAvailable ? undefined : true
    })),

  toggleDeliveryAvailable: () =>
    set((state) => ({
      deliveryAvailable: state.deliveryAvailable ? undefined : true
    })),

  resetFilters: () => set(initialState)
}));
