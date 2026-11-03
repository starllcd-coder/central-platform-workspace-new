import { businessTrustItems } from "@/features/business/data/business-marketing-data";
import { SectionHeading } from "@/components/layout/section-heading";
import { SectionShell } from "@/components/layout/section-shell";
import { PremiumFeatureCard } from "@/components/blocks/premium-feature-card";

export function BusinessTrustSection() {
  return (
    <SectionShell background="default">
      <SectionHeading
        eyebrow="Business Model"
        title="Built for growth, not locked pricing."
        description="Pricing, commissions, subscriptions, promotions, marketplace visibility, and country-specific rules must remain dynamic."
        align="center"
      />

      <div className="mt-12 grid gap-5 md:grid-cols-3">
        {businessTrustItems.map((item) => (
          <PremiumFeatureCard
            key={item.title}
            title={item.title}
            description={item.description}
            icon={item.icon}
            tone="gold"
          />
        ))}
      </div>
    </SectionShell>
  );
}
