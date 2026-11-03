import { cn } from "@/lib/utils";

type BrandMarkProps = {
  className?: string;
  showText?: boolean;
};

export function BrandMark({ className, showText = true }: BrandMarkProps) {
  return (
    <div className={cn("inline-flex items-center gap-3", className)}>
      <div className="relative flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl bg-midnight-gradient shadow-soft">
        <span className="absolute inset-0 bg-gold-gradient opacity-20" />
        <span className="relative font-heading text-lg font-bold text-white">N</span>
      </div>

      {showText ? (
        <div className="leading-none">
          <div className="font-heading text-xl font-bold tracking-tight text-luxury-ink dark:text-white">
            Nexivo
          </div>
          <div className="mt-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-luxury-gold">
            by DSS
          </div>
        </div>
      ) : null}
    </div>
  );
}
