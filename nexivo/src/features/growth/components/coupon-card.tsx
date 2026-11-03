"use client";

import { TicketPercent } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Coupon } from "@/features/growth/types/growth.types";
import { useCouponStore } from "@/features/growth/store/coupon.store";

type CouponCardProps = {
  coupon: Coupon;
};

export function CouponCard({ coupon }: CouponCardProps) {
  const { appliedCoupon, applyCoupon, removeCoupon } = useCouponStore();
  const applied = appliedCoupon?.id === coupon.id;

  return (
    <article className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="flex items-start justify-between gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
          <TicketPercent size={24} />
        </div>

        <Badge variant={coupon.active ? "success" : "secondary"}>
          {coupon.active ? "Active" : "Inactive"}
        </Badge>
      </div>

      <h3 className="mt-6 font-heading text-2xl font-semibold text-luxury-ink">
        {coupon.title}
      </h3>

      <p className="mt-3 text-sm leading-7 text-slate-600">{coupon.description}</p>

      <div className="mt-5 rounded-3xl border border-dashed border-brand-200 bg-brand-50 px-4 py-3 text-center">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-brand-700">
          Coupon Code
        </p>
        <p className="mt-1 font-heading text-2xl font-semibold text-brand-800">
          {coupon.code}
        </p>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        <Badge variant="outline">{coupon.serviceScope}</Badge>
        <Badge variant="gold">{coupon.valueLabel}</Badge>
        <Badge variant="secondary">Expires {coupon.expiryDate}</Badge>
      </div>

      <Button
        variant={applied ? "outline" : "luxury"}
        className="mt-6"
        fullWidth
        onClick={() => (applied ? removeCoupon() : applyCoupon(coupon))}
      >
        {applied ? "Remove Coupon" : "Apply Coupon"}
      </Button>
    </article>
  );
}
