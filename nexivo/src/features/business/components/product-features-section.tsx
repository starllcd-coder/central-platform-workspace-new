import { SectionHeading } from "@/components/layout/section-heading";
import { SectionShell } from "@/components/layout/section-shell";
import { PremiumFeatureCard } from "@/components/blocks/premium-feature-card";

type ProductFeature = {
  title: string;
  description: string;
  icon: React.ElementType;
};

type ProductFeaturesSectionProps = {
  eyebrow: string;
  title: string;
  description: string;
  features: readonly ProductFeature[];
};

export function ProductFeaturesSection({
  eyebrow,
  title,
  description,
  features
}: ProductFeaturesSectionProps) {
  return (
    <SectionShell background="default">
      <SectionHeading
        eyebrow={eyebrow}
        title={title}
        description={description}
        align="center"
      />

      <div className="mt-12 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {features.map((feature) => (
          <PremiumFeatureCard
            key={feature.title}
            title={feature.title}
            description={feature.description}
            icon={feature.icon}
            tone="blue"
          />
        ))}
      </div>
    </SectionShell>
  );
}
