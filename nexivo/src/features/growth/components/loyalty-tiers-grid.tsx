import { loyaltyTiers } from "@/features/growth/data/growth-data";
import { LoyaltyTierCard } from "@/features/growth/components/loyalty-tier-card";

export function LoyaltyTiersGrid() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {loyaltyTiers.map((tier, index) => (
            <LoyaltyTierCard key={tier.tier} tier={tier} current={index === 0} />
          ))}
        </div>
      </div>
    </section>
  );
}
