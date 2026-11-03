import { cn } from "@/lib/utils";

type MetricCardProps = {
  label: string;
  value: string;
  description?: string;
  className?: string;
};

export function MetricCard({ label, value, description, className }: MetricCardProps) {
  return (
    <div
      className={cn(
        "rounded-4xl border border-white/70 bg-white/85 p-6 shadow-premium backdrop-blur-xl",
        className
      )}
    >
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <div className="mt-3 font-heading text-4xl font-semibold tracking-tight text-luxury-ink">
        {value}
      </div>
      {description ? <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p> : null}
    </div>
  );
}
