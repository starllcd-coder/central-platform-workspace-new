import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type PageHeroProps = {
  eyebrow?: string;
  title: string;
  description: string;
  primaryLabel?: string;
  primaryHref?: string;
  secondaryLabel?: string;
  secondaryHref?: string;
  spacing?: "default" | "compact";
};

export function PageHero({
  eyebrow,
  title,
  description,
  primaryLabel,
  primaryHref,
  secondaryLabel,
  secondaryHref,
  spacing = "default"
}: PageHeroProps) {
  return (
    <section className="bg-nexivo-radial">
      <div
        className={cn(
          "nexivo-container",
          spacing === "compact" ? "py-10 md:py-14" : "py-12 md:py-16"
        )}
      >
        <div className="max-w-4xl">
          {eyebrow ? <p className="eyebrow mb-5">{eyebrow}</p> : null}

          <h1 className="font-heading text-5xl font-semibold tracking-tight text-luxury-ink md:text-7xl">
            {title}
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            {description}
          </p>

          {(primaryLabel && primaryHref) || (secondaryLabel && secondaryHref) ? (
            <div className="mt-9 flex flex-wrap gap-3">
              {primaryLabel && primaryHref ? (
                <Button asChild variant="luxury" size="lg">
                  <a href={primaryHref}>
                    {primaryLabel}
                    <ArrowRight className="ml-2" size={18} />
                  </a>
                </Button>
              ) : null}

              {secondaryLabel && secondaryHref ? (
                <Button asChild variant="outline" size="lg">
                  <a href={secondaryHref}>{secondaryLabel}</a>
                </Button>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
