"use client";

import { create } from "zustand";

type WishlistStore = {
  wishlistIds: string[];
  toggleWishlist: (id: string) => void;
  isWishlisted: (id: string) => boolean;
};

export const useWishlistStore = create<WishlistStore>((set, get) => ({
  wishlistIds: ["wish-001", "wish-002", "wish-003"],

  toggleWishlist: (id) =>
    set((state) => ({
      wishlistIds: state.wishlistIds.includes(id)
        ? state.wishlistIds.filter((item) => item !== id)
        : [...state.wishlistIds, id]
    })),

  isWishlisted: (id) => get().wishlistIds.includes(id)
}));
