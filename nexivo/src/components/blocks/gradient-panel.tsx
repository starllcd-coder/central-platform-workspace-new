import { cn } from "@/lib/utils";

type GradientPanelProps = {
  children: React.ReactNode;
  className?: string;
};

export function GradientPanel({ children, className }: GradientPanelProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-4xl bg-luxury-gradient p-8 shadow-premium md:p-10",
        className
      )}
    >
      <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-brand-500/10 blur-3xl" />
      <div className="absolute -bottom-24 -left-20 h-72 w-72 rounded-full bg-luxury-gold/20 blur-3xl" />
      <div className="relative">{children}</div>
    </div>
  );
}
