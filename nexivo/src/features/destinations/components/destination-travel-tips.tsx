import { Lightbulb } from "lucide-react";
import type { DestinationGuide } from "@/features/destinations/types/destination.types";

type DestinationTravelTipsProps = {
  destination: DestinationGuide;
};

export function DestinationTravelTips({ destination }: DestinationTravelTipsProps) {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-8">
          <p className="eyebrow mb-5">Travel Tips</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Smart planning for {destination.city}.
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-8 text-slate-600">
            These destination tips help customers understand how stays, cars, and laundry services
            work together in the Nexivo journey.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {destination.travelTips.map((tip) => (
            <div
              key={tip}
              className="flex gap-4 rounded-4xl border border-slate-200 bg-white p-5 shadow-soft"
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-3xl bg-luxury-gold/15 text-luxury-bronze">
                <Lightbulb size={21} />
              </div>

              <p className="text-sm leading-7 text-slate-700">{tip}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
