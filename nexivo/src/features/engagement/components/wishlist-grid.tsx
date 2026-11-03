import { wishlistItems } from "@/features/engagement/data/engagement-data";
import { WishlistCard } from "@/features/engagement/components/wishlist-card";

export function WishlistGrid() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="grid gap-6 md:grid-cols-3">
          {wishlistItems.map((item) => (
            <WishlistCard key={item.id} item={item} />
          ))}
        </div>
      </div>
    </section>
  );
}
