import { CheckCircle2 } from "lucide-react";
import type { LaundryProvider } from "@/features/laundry/types/laundry.types";
import { laundryFeatureLabels, laundryServiceTypeLabels } from "@/features/laundry/data/laundry-labels";
import { formatMoney } from "@/features/currency/utils/currency-utils";

type LaundryProviderOverviewProps = {
  provider: LaundryProvider;
};

export function LaundryProviderOverview({ provider }: LaundryProviderOverviewProps) {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container grid gap-8 lg:grid-cols-[1fr_360px]">
        <div>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink">
            Provider overview
          </h2>

          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
            {provider.shortDescription} Laundrex provider pages are prepared for service catalog,
            pickup scheduling, delivery tracking, customer order history, branch operations, and
            Nexivo cross-selling after stays and car bookings.
          </p>

          <h3 className="mt-8 font-heading text-xl font-semibold text-luxury-ink">
            Available services
          </h3>

          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {provider.serviceTypes.map((serviceType) => (
              <div
                key={serviceType}
                className="flex items-center gap-3 rounded-3xl border border-slate-200 bg-white px-4 py-3 shadow-soft"
              >
                <CheckCircle2 size={18} className="text-emerald-600" />
                <span className="text-sm font-semibold text-slate-700">
                  {laundryServiceTypeLabels[serviceType]}
                </span>
              </div>
            ))}
          </div>

          <h3 className="mt-8 font-heading text-xl font-semibold text-luxury-ink">
            Features
          </h3>

          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {provider.features.map((feature) => (
              <div
                key={feature}
                className="flex items-center gap-3 rounded-3xl border border-slate-200 bg-white px-4 py-3 shadow-soft"
              >
                <CheckCircle2 size={18} className="text-emerald-600" />
                <span className="text-sm font-semibold text-slate-700">
                  {laundryFeatureLabels[feature]}
                </span>
              </div>
            ))}
          </div>
        </div>

        <aside className="h-fit rounded-4xl border border-slate-200 bg-luxury-mist p-6 shadow-soft">
          <h3 className="font-heading text-xl font-semibold text-luxury-ink">
            Order policies
          </h3>

          <div className="mt-5 space-y-4 text-sm leading-6 text-slate-600">
            <p>
              <strong className="text-luxury-ink">Minimum order:</strong>{" "}
              {formatMoney(provider.minimumOrder, provider.currency)}
            </p>
            <p>
              <strong className="text-luxury-ink">Pickup:</strong>{" "}
              {provider.pickupAvailable ? "Available" : "Not available"}
            </p>
            <p>
              <strong className="text-luxury-ink">Delivery:</strong>{" "}
              {provider.deliveryAvailable ? "Available" : "Not available"}
            </p>
            <p>
              <strong className="text-luxury-ink">Payment:</strong> Online payment and
              pay-on-delivery options can be configured per provider.
            </p>
          </div>
        </aside>
      </div>
    </section>
  );
}
