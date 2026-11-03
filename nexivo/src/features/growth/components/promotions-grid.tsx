import { promotions } from "@/features/growth/data/growth-data";
import { PromotionCard } from "@/features/growth/components/promotion-card";

export function PromotionsGrid() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="grid gap-6 md:grid-cols-3">
          {promotions.map((promotion) => (
            <PromotionCard key={promotion.id} promotion={promotion} />
          ))}
        </div>
      </div>
    </section>
  );
}
