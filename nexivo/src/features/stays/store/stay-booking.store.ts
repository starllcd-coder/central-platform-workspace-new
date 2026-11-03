"use client";

import { create } from "zustand";
import type { StayBookingDraft } from "@/features/stays/types/stay-booking.types";

type StayBookingStore = {
  draft: StayBookingDraft | null;
  startBooking: (draft: StayBookingDraft) => void;
  updateDraft: (payload: Partial<StayBookingDraft>) => void;
  clearDraft: () => void;
};

export const useStayBookingStore = create<StayBookingStore>((set) => ({
  draft: null,

  startBooking: (draft) => set({ draft }),

  updateDraft: (payload) =>
    set((state) => ({
      draft: state.draft ? { ...state.draft, ...payload } : null
    })),

  clearDraft: () => set({ draft: null })
}));
