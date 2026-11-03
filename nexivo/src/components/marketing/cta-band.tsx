import { ArrowRight, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type CtaBandProps = {
  title: string;
  description: string;
  primaryLabel: string;
  primaryHref: string;
  secondaryLabel?: string;
  secondaryHref?: string;
  className?: string;
};

export function CtaBand({
  title,
  description,
  primaryLabel,
  primaryHref,
  secondaryLabel,
  secondaryHref,
  className
}: CtaBandProps) {
  return (
    <section
      className={cn(
        "relative overflow-hidden rounded-4xl bg-midnight-gradient p-8 text-white shadow-premium md:p-12",
        className
      )}
    >
      <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-luxury-gold/20 blur-3xl" />
      <div className="absolute -bottom-20 left-10 h-72 w-72 rounded-full bg-brand-500/20 blur-3xl" />

      <div className="relative grid gap-8 lg:grid-cols-[1.35fr_0.85fr] lg:items-center">
        <div>
          <p className="mb-4 inline-flex rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-semibold text-luxury-dune">
            Nexivo by DSS
          </p>

          <h2 className="max-w-3xl font-heading text-3xl font-semibold tracking-tight md:text-5xl">
            {title}
          </h2>

          <p className="mt-5 max-w-2xl text-base leading-8 text-white/74">{description}</p>

          <div className="mt-6 grid max-w-2xl gap-3 sm:grid-cols-2">
            {["Book your stay", "Rent your car", "Manage your laundry", "All from one platform"].map((item) => (
              <div key={item} className="flex items-center gap-2 text-sm font-semibold text-white/85">
                <CheckCircle2 size={17} className="text-luxury-dune" />
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row lg:justify-end">
          <Button asChild variant="gold" size="lg">
            <a href={primaryHref}>
              {primaryLabel}
              <ArrowRight className="ml-2" size={18} />
            </a>
          </Button>

          {secondaryLabel && secondaryHref ? (
            <Button asChild variant="outline" size="lg" className="border-white/20 bg-white/10 text-white hover:bg-white/15">
              <a href={secondaryHref}>{secondaryLabel}</a>
            </Button>
          ) : null}
        </div>
      </div>
    </section>
  );
}