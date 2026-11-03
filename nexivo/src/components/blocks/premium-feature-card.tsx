import { cn } from "@/lib/utils";

type PremiumFeatureCardProps = {
  title: string;
  description: string;
  icon: React.ElementType;
  tone?: "blue" | "dark" | "gold" | "green" | "neutral";
  className?: string;
};

export function PremiumFeatureCard({
  title,
  description,
  icon: Icon,
  tone = "neutral",
  className
}: PremiumFeatureCardProps) {
  const toneClass = {
    blue: "bg-brand-50 text-brand-700",
    dark: "bg-luxury-ink text-white",
    gold: "bg-luxury-gold/15 text-luxury-bronze",
    green: "bg-emerald-50 text-emerald-700",
    neutral: "bg-slate-100 text-slate-700"
  }[tone];

  return (
    <article
      className={cn(
        "group rounded-4xl border border-slate-200 bg-white p-6 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium",
        className
      )}
    >
      <div className={cn("mb-6 flex h-14 w-14 items-center justify-center rounded-3xl", toneClass)}>
        <Icon size={24} />
      </div>

      <h3 className="font-heading text-xl font-semibold tracking-tight text-luxury-ink">
        {title}
      </h3>

      <p className="mt-3 text-sm leading-7 text-slate-600">{description}</p>
    </article>
  );
}
