"use client";

import { create } from "zustand";
import type { Coupon } from "@/features/growth/types/growth.types";

type CouponStore = {
  appliedCoupon: Coupon | null;
  applyCoupon: (coupon: Coupon) => void;
  removeCoupon: () => void;
};

export const useCouponStore = create<CouponStore>((set) => ({
  appliedCoupon: null,

  applyCoupon: (coupon) => set({ appliedCoupon: coupon }),

  removeCoupon: () => set({ appliedCoupon: null })
}));
