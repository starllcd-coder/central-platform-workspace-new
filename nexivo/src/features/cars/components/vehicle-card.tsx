import { Briefcase, Car, Fuel, Heart, MapPin, ShieldCheck, Star, UsersRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { RentalVehicle } from "@/features/cars/types/cars.types";
import { vehicleCategoryLabels } from "@/features/cars/data/car-labels";
import { formatMoney } from "@/features/currency/utils/currency-utils";

type VehicleCardProps = {
  vehicle: RentalVehicle;
};

export function VehicleCard({ vehicle }: VehicleCardProps) {
  return (
    <article className="group overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-premium">
      <div className="relative h-64 overflow-hidden">
        <img
          src={vehicle.imageUrl}
          alt={vehicle.name}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />

        <div className="absolute left-4 top-4 flex flex-wrap gap-2">
          {vehicle.featured ? <Badge variant="gold">Featured</Badge> : null}
          {vehicle.verified ? (
            <Badge variant="success">
              <ShieldCheck className="mr-1" size={13} />
              Verified
            </Badge>
          ) : null}
        </div>

        <button className="absolute right-4 top-4 flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-slate-700 shadow-soft transition-colors hover:text-red-500">
          <Heart size={18} />
        </button>
      </div>

      <div className="p-6">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline">{vehicleCategoryLabels[vehicle.category]}</Badge>
          {vehicle.payAtPickup ? <Badge variant="secondary">Pay at pickup</Badge> : null}
          {vehicle.freeCancellation ? <Badge variant="secondary">Free cancellation</Badge> : null}
        </div>

        <h3 className="mt-4 font-heading text-2xl font-semibold tracking-tight text-luxury-ink">
          {vehicle.name}
        </h3>

        <p className="mt-1 text-sm font-semibold text-brand-700">{vehicle.companyName}</p>

        <div className="mt-3 flex items-center gap-2 text-sm text-slate-600">
          <MapPin size={16} />
          <span>
            {vehicle.pickupLocation}, {vehicle.city}, {vehicle.country}
          </span>
        </div>

        <p className="mt-4 text-sm leading-7 text-slate-600">{vehicle.shortDescription}</p>

        <div className="mt-5 grid grid-cols-2 gap-3 text-sm text-slate-600 md:grid-cols-4">
          <span className="inline-flex items-center gap-2">
            <UsersRound size={15} />
            {vehicle.seats} seats
          </span>
          <span className="inline-flex items-center gap-2">
            <Briefcase size={15} />
            {vehicle.bags} bags
          </span>
          <span className="inline-flex items-center gap-2">
            <Car size={15} />
            {vehicle.transmission}
          </span>
          <span className="inline-flex items-center gap-2">
            <Fuel size={15} />
            {vehicle.fuelType}
          </span>
        </div>

        <div className="mt-6 flex items-center justify-between gap-4 border-t border-slate-200 pt-5">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
              <Star size={16} className="fill-luxury-gold text-luxury-gold" />
              {vehicle.rating}
              <span className="text-slate-400">({vehicle.reviewCount} reviews)</span>
            </div>

            <div className="mt-2">
              <span className="font-heading text-2xl font-semibold text-luxury-ink">
                {formatMoney(vehicle.pricePerDay, vehicle.currency)}
              </span>
              <span className="text-sm text-slate-500"> / day</span>
            </div>
          </div>

          <Button asChild variant="luxury">
            <a href={`/cars/${vehicle.slug}`}>View</a>
          </Button>
        </div>
      </div>
    </article>
  );
}
