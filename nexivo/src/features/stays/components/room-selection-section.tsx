import type { StayProperty } from "@/features/stays/types/stays.types";
import { getRoomsByPropertyId } from "@/features/stays/data/stay-rooms";
import { RoomSelectionCard } from "@/features/stays/components/room-selection-card";
import type { StayRoom } from "@/features/stays/types/stay-booking.types";

type RoomSelectionSectionProps = {
  property: StayProperty;
};

export function RoomSelectionSection({ property }: RoomSelectionSectionProps) {
  const centralRoom: StayRoom | null = property.providerResourceId
    ? {
        id: property.providerResourceId,
        propertyId: property.id,
        name: property.providerResourceName || "Available unit",
        slug: property.providerResourceId,
        description: property.shortDescription,
        maxGuests: 4,
        bedType: "Provider configured",
        size: "Provider inventory",
        pricePerNight: property.pricePerNight,
        currency: property.currency,
        refundable: property.freeCancellation,
        breakfastIncluded: false,
        availableUnits: 1,
        imageUrl: property.imageUrl
      }
    : null;
  const rooms = getRoomsByPropertyId(property.id);
  const displayedRooms = rooms.length > 0 ? rooms : centralRoom ? [centralRoom] : [];

  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="mb-8">
          <p className="eyebrow mb-5">Rooms & Units</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Select your room or unit.
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-8 text-slate-600">
            Room inventory is prepared to connect with StayLux availability, pricing, policies,
            payment options, and central Nexivo booking flow.
          </p>
        </div>

        <div className="space-y-5">
          {displayedRooms.map((room) => (
            <RoomSelectionCard key={room.id} room={room} propertySlug={property.slug} />
          ))}
        </div>
      </div>
    </section>
  );
}
