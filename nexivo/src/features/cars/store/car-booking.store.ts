"use client";

import { create } from "zustand";
import type { CarBookingDraft } from "@/features/cars/types/car-booking.types";

type CarBookingStore = {
  draft: CarBookingDraft | null;
  startBooking: (draft: CarBookingDraft) => void;
  updateDraft: (payload: Partial<CarBookingDraft>) => void;
  clearDraft: () => void;
};

export const useCarBookingStore = create<CarBookingStore>((set) => ({
  draft: null,

  startBooking: (draft) => set({ draft }),

  updateDraft: (payload) =>
    set((state) => ({
      draft: state.draft ? { ...state.draft, ...payload } : null
    })),

  clearDraft: () => set({ draft: null })
}));
