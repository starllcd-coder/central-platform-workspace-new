import { DestinationCard } from "@/features/destinations/components/destination-card";
import { getFeaturedDestinationGuides } from "@/features/destinations/utils/destination-utils";

export function DestinationGrid() {
  const destinations = getFeaturedDestinationGuides();

  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {destinations.map((destination) => (
            <DestinationCard key={destination.slug} destination={destination} />
          ))}
        </div>
      </div>
    </section>
  );
}
