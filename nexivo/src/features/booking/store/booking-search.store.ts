"use client";

import { create } from "zustand";
import type { BookingSearchState } from "@/features/booking/types/booking.types";

type BookingSearchStore = BookingSearchState & {
  setService: (service: BookingSearchState["service"]) => void;
  updateSearch: (payload: Partial<BookingSearchState>) => void;
  resetSearch: () => void;
};

const initialState: BookingSearchState = {
  service: "stays",
  destination: "Salalah",
  checkIn: "",
  checkOut: "",
  guests: 2,
  pickupDate: "",
  returnDate: "",
  pickupLocation: "Salalah Airport",
  laundryDate: "",
  laundryAddress: ""
};

export const useBookingSearchStore = create<BookingSearchStore>((set) => ({
  ...initialState,

  setService: (service) => set({ service }),

  updateSearch: (payload) => set((state) => ({ ...state, ...payload })),

  resetSearch: () => set(initialState)
}));
