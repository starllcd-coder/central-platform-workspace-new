import { coupons } from "@/features/growth/data/growth-data";
import { CouponCard } from "@/features/growth/components/coupon-card";

export function CouponsGrid() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {coupons.map((coupon) => (
            <CouponCard key={coupon.id} coupon={coupon} />
          ))}
        </div>
      </div>
    </section>
  );
}
