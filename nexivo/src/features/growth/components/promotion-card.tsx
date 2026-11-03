import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Promotion } from "@/features/growth/types/growth.types";

type PromotionCardProps = {
  promotion: Promotion;
};

export function PromotionCard({ promotion }: PromotionCardProps) {
  return (
    <article className="group overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium">
      <div className="relative h-52 overflow-hidden">
        <img
          src={promotion.imageUrl}
          alt={promotion.title}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />

        <div className="absolute left-4 top-4">
          <Badge variant="gold">{promotion.badge}</Badge>
        </div>
      </div>

      <div className="p-6">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-brand-700">
          {promotion.serviceScope} • {promotion.location}
        </p>

        <h3 className="mt-3 font-heading text-2xl font-semibold text-luxury-ink">
          {promotion.title}
        </h3>

        <p className="mt-3 text-sm leading-7 text-slate-600">{promotion.description}</p>

        <Button asChild variant="outline" className="mt-6">
          <a href={promotion.href}>
            Explore Promotion
            <ArrowRight className="ml-2 transition-transform group-hover:translate-x-1" size={17} />
          </a>
        </Button>
      </div>
    </article>
  );
}
