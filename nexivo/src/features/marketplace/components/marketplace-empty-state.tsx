import { SearchX } from "lucide-react";
import { Button } from "@/components/ui/button";

type MarketplaceEmptyStateProps = {
  title?: string;
  description?: string;
  actionHref?: string;
  actionLabel?: string;
};

export function MarketplaceEmptyState({
  title = "No matching results found",
  description = "Try changing your destination, dates, category, or service filters.",
  actionHref = "/destinations",
  actionLabel = "Explore Destinations"
}: MarketplaceEmptyStateProps) {
  return (
    <div className="rounded-4xl border border-dashed border-slate-300 bg-white p-10 text-center shadow-soft">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
        <SearchX size={28} />
      </div>
      <h3 className="mt-6 font-heading text-2xl font-semibold text-luxury-ink">{title}</h3>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-600">{description}</p>
      <Button asChild variant="luxury" className="mt-6">
        <a href={actionHref}>{actionLabel}</a>
      </Button>
    </div>
  );
}