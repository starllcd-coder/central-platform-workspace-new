"use client";

import { Heart, MapPin, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { WishlistItem } from "@/features/engagement/types/engagement.types";
import { useWishlistStore } from "@/features/engagement/store/wishlist.store";

type WishlistCardProps = {
  item: WishlistItem;
};

export function WishlistCard({ item }: WishlistCardProps) {
  const { toggleWishlist, isWishlisted } = useWishlistStore();
  const active = isWishlisted(item.id);

  return (
    <article className="group overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium">
      <div className="relative h-52 overflow-hidden">
        <img
          src={item.imageUrl}
          alt={item.title}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />

        <button
          type="button"
          onClick={() => toggleWishlist(item.id)}
          className="absolute right-4 top-4 flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-red-500 shadow-soft"
        >
          <Heart size={18} className={active ? "fill-red-500" : ""} />
        </button>
      </div>

      <div className="p-6">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-brand-700">
          {item.serviceType}
        </p>

        <h3 className="mt-2 font-heading text-2xl font-semibold text-luxury-ink">
          {item.title}
        </h3>

        <p className="mt-3 flex items-center gap-2 text-sm text-slate-600">
          <MapPin size={16} />
          {item.location}
        </p>

        <div className="mt-4 flex items-center justify-between gap-4">
          <span className="font-semibold text-luxury-ink">{item.priceLabel}</span>
          <span className="inline-flex items-center gap-1 text-sm font-semibold text-slate-700">
            <Star size={15} className="fill-luxury-gold text-luxury-gold" />
            {item.rating}
          </span>
        </div>

        <Button asChild variant="outline" className="mt-5" fullWidth>
          <a href={item.href}>View Details</a>
        </Button>
      </div>
    </article>
  );
}
