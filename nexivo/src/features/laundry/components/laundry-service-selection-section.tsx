import type { LaundryProvider } from "@/features/laundry/types/laundry.types";
import { getLaundryServicesByProvider } from "@/features/laundry/data/laundry-services";
import { LaundryServiceSelectionCard } from "@/features/laundry/components/laundry-service-selection-card";
import type { LaundryServiceItem } from "@/features/laundry/types/laundry.types";

type LaundryServiceSelectionSectionProps = {
  provider: LaundryProvider;
};

export function LaundryServiceSelectionSection({
  provider
}: LaundryServiceSelectionSectionProps) {
  const centralService: LaundryServiceItem | null = provider.providerResourceId
    ? {
        id: provider.providerResourceId,
        providerId: provider.id,
        name: provider.providerResourceName || "Laundry service",
        serviceType: "wash-fold",
        description: provider.shortDescription,
        price: provider.minimumOrder,
        unit: provider.providerResourceUnit || "order",
        currency: provider.currency,
        estimatedTime: "Provider schedule"
      }
    : null;
  const services = getLaundryServicesByProvider(provider.id);
  const displayedServices = services.length > 0 ? services : centralService ? [centralService] : [];

  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="mb-8">
          <p className="eyebrow mb-5">Service Catalog</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Select laundry services.
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-8 text-slate-600">
            Laundrex service catalog is prepared for pickup scheduling, item quantities,
            delivery tracking, provider pricing, and future customer subscriptions.
          </p>
        </div>

        <div className="space-y-5">
          {displayedServices.map((service) => (
            <LaundryServiceSelectionCard
              key={service.id}
              provider={provider}
              service={service}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
