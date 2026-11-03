import { CheckCircle2 } from "lucide-react";
import type { RentalVehicle } from "@/features/cars/types/cars.types";
import { vehicleFeatureLabels } from "@/features/cars/data/car-labels";
import { getVehiclePolicy } from "@/features/cars/data/vehicle-policies";

type VehicleOverviewProps = {
  vehicle: RentalVehicle;
};

export function VehicleOverview({ vehicle }: VehicleOverviewProps) {
  const policy = getVehiclePolicy(vehicle.id);

  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container grid gap-8 lg:grid-cols-[1fr_360px]">
        <div>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink">
            Vehicle overview
          </h2>

          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
            {vehicle.shortDescription} Nexivo vehicle pages are prepared for DriveSphere fleet
            availability, branch workflow, driver requirements, rental terms, verified reviews, and
            future hotel booking cross-sells.
          </p>

          <div className="mt-8 grid gap-3 md:grid-cols-2">
            {vehicle.features.map((feature) => (
              <div
                key={feature}
                className="flex items-center gap-3 rounded-3xl border border-slate-200 bg-white px-4 py-3 shadow-soft"
              >
                <CheckCircle2 size={18} className="text-emerald-600" />
                <span className="text-sm font-semibold text-slate-700">
                  {vehicleFeatureLabels[feature]}
                </span>
              </div>
            ))}
          </div>
        </div>

        <aside className="h-fit rounded-4xl border border-slate-200 bg-luxury-mist p-6 shadow-soft">
          <h3 className="font-heading text-xl font-semibold text-luxury-ink">
            Rental policies
          </h3>

          <div className="mt-5 space-y-4 text-sm leading-6 text-slate-600">
            <p>
              <strong className="text-luxury-ink">Minimum age:</strong>{" "}
              {policy?.minimumAge ?? 21} years
            </p>
            <p>
              <strong className="text-luxury-ink">Deposit:</strong>{" "}
              {policy?.depositRequired ? "Required" : "Not required"}
            </p>
            <p>
              <strong className="text-luxury-ink">Mileage:</strong>{" "}
              {policy?.mileagePolicy ?? "Mileage policy depends on rental provider."}
            </p>
            <p>
              <strong className="text-luxury-ink">Fuel:</strong>{" "}
              {policy?.fuelPolicy ?? "Return with same fuel level."}
            </p>
            <p>
              <strong className="text-luxury-ink">Insurance:</strong>{" "}
              {policy?.insurancePolicy ?? "Insurance terms depend on provider."}
            </p>
            <p>
              <strong className="text-luxury-ink">Cancellation:</strong>{" "}
              {policy?.cancellationPolicy ?? "Cancellation rules depend on provider."}
            </p>
          </div>
        </aside>
      </div>
    </section>
  );
}
