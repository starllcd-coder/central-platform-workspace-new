"use client";

import { Clock, Plus, Shirt } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { LaundryProvider, LaundryServiceItem } from "@/features/laundry/types/laundry.types";
import { useLaundryOrderStore } from "@/features/laundry/store/laundry-order.store";
import { formatMoney } from "@/features/currency/utils/currency-utils";
import { laundryServiceTypeLabels } from "@/features/laundry/data/laundry-labels";

type LaundryServiceSelectionCardProps = {
  provider: LaundryProvider;
  service: LaundryServiceItem;
};

export function LaundryServiceSelectionCard({
  provider,
  service
}: LaundryServiceSelectionCardProps) {
  const { startOrder } = useLaundryOrderStore();

  function handleStartOrder() {
    const today = new Date().toISOString().slice(0, 10);

    startOrder({
      providerId: provider.id,
      selectedItems: [
        {
          serviceItemId: service.id,
          quantity: 1
        }
      ],
      pickupDate: today,
      paymentMethod: "pay-on-delivery"
    });

    window.location.href = `/laundry/providers/${provider.slug}/order?service=${service.id}`;
  }

  return (
    <article className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="flex flex-wrap items-start justify-between gap-5">
        <div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">{laundryServiceTypeLabels[service.serviceType]}</Badge>
            <Badge variant="secondary">{service.unit}</Badge>
          </div>

          <h3 className="mt-4 font-heading text-2xl font-semibold text-luxury-ink">
            {service.name}
          </h3>

          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
            {service.description}
          </p>

          <div className="mt-5 flex flex-wrap gap-3 text-sm text-slate-600">
            <span className="inline-flex items-center gap-2">
              <Clock size={16} />
              {service.estimatedTime}
            </span>
            <span className="inline-flex items-center gap-2">
              <Shirt size={16} />
              Charged per {service.unit}
            </span>
          </div>
        </div>

        <div className="min-w-[160px] text-left md:text-right">
          <div className="font-heading text-3xl font-semibold text-luxury-ink">
            {formatMoney(service.price, service.currency)}
          </div>
          <p className="text-sm text-slate-500">per {service.unit}</p>

          <Button variant="luxury" className="mt-5" onClick={handleStartOrder}>
            <Plus className="mr-2" size={17} />
            Start Order
          </Button>
        </div>
      </div>
    </article>
  );
}
