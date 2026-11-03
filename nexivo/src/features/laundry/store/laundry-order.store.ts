"use client";

import { create } from "zustand";
import type { LaundryOrderDraft } from "@/features/laundry/types/laundry.types";

type LaundryOrderStore = {
  draft: LaundryOrderDraft | null;
  startOrder: (draft: LaundryOrderDraft) => void;
  updateDraft: (payload: Partial<LaundryOrderDraft>) => void;
  clearDraft: () => void;
};

export const useLaundryOrderStore = create<LaundryOrderStore>((set) => ({
  draft: null,

  startOrder: (draft) => set({ draft }),

  updateDraft: (payload) =>
    set((state) => ({
      draft: state.draft ? { ...state.draft, ...payload } : null
    })),

  clearDraft: () => set({ draft: null })
}));
