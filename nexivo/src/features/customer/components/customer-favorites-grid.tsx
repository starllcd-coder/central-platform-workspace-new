import { Heart } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CustomerFavorite } from "@/features/customer/types/customer.types";

type CustomerFavoritesGridProps = {
  favorites: CustomerFavorite[];
};

export function CustomerFavoritesGrid({ favorites }: CustomerFavoritesGridProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Favorites</CardTitle>
        <p className="text-sm text-slate-600">
          Saved hotels, cars, laundry providers, and future destinations.
        </p>
      </CardHeader>

      <CardContent>
        <div className="grid gap-5 md:grid-cols-3">
          {favorites.map((favorite) => (
            <a
              key={favorite.id}
              href={favorite.href}
              className="group overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-soft transition-all hover:-translate-y-1 hover:shadow-premium"
            >
              <div className="relative h-40">
                <img
                  src={favorite.imageUrl}
                  alt={favorite.title}
                  className="h-full w-full object-cover"
                />
                <div className="absolute right-3 top-3 flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-red-500 shadow-soft">
                  <Heart size={18} />
                </div>
              </div>

              <div className="p-4">
                <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                  {favorite.title}
                </h3>
                <p className="mt-1 text-sm text-slate-600">{favorite.location}</p>
              </div>
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
