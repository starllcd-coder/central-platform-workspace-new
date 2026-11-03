import { Briefcase, Car, Fuel, MapPin, ShieldCheck, Star, UsersRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { RentalVehicle } from "@/features/cars/types/cars.types";
import { vehicleCategoryLabels } from "@/features/cars/data/car-labels";

type VehicleHeroProps = {
  vehicle: RentalVehicle;
};

export function VehicleHero({ vehicle }: VehicleHeroProps) {
  return (
    <section className="bg-luxury-gradient">
      <div className="nexivo-container py-10 md:py-14">
        <div className="grid gap-6 lg:grid-cols-[1fr_0.8fr]">
          <div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">{vehicleCategoryLabels[vehicle.category]}</Badge>
              {vehicle.verified ? (
                <Badge variant="success">
                  <ShieldCheck className="mr-1" size={13} />
                  Verified Partner
                </Badge>
              ) : null}
              {vehicle.featured ? <Badge variant="gold">Featured</Badge> : null}
            </div>

            <h1 className="mt-5 font-heading text-4xl font-semibold tracking-tight text-luxury-ink md:text-6xl">
              {vehicle.name}
            </h1>

            <p className="mt-2 text-base font-semibold text-brand-700">{vehicle.companyName}</p>

            <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-slate-600">
              <span className="inline-flex items-center gap-2">
                <MapPin size={17} />
                {vehicle.pickupLocation}, {vehicle.city}, {vehicle.country}
              </span>

              <span className="inline-flex items-center gap-2 font-semibold text-slate-700">
                <Star size={17} className="fill-luxury-gold text-luxury-gold" />
                {vehicle.rating} ({vehicle.reviewCount} reviews)
              </span>
            </div>

            <p className="mt-6 max-w-3xl text-base leading-8 text-slate-600">
              {vehicle.shortDescription}
            </p>

            <div className="mt-8 grid max-w-3xl grid-cols-2 gap-3 md:grid-cols-4">
              <VehicleSpec icon={UsersRound} label="Seats" value={`${vehicle.seats}`} />
              <VehicleSpec icon={Briefcase} label="Bags" value={`${vehicle.bags}`} />
              <VehicleSpec icon={Car} label="Transmission" value={vehicle.transmission} />
              <VehicleSpec icon={Fuel} label="Fuel" value={vehicle.fuelType} />
            </div>
          </div>

          <div className="rounded-4xl border border-white/70 bg-white/70 p-3 shadow-premium backdrop-blur-xl">
            <img
              src={vehicle.imageUrl}
              alt={vehicle.name}
              className="h-full min-h-[360px] w-full rounded-3xl object-cover"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

function VehicleSpec({
  icon: Icon,
  label,
  value
}: {
  icon: React.ElementType;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-3xl border border-white/70 bg-white/80 p-4 shadow-soft">
      <Icon size={20} className="text-brand-700" />
      <p className="mt-3 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-sm font-semibold capitalize text-luxury-ink">{value}</p>
    </div>
  );
}
