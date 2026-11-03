import { ArrowRight, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { contactChannels } from "@/features/support/data/support-data";

export function ContactChannelsGrid() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="grid gap-6 md:grid-cols-3">
          {contactChannels.map((channel) => (
            <article
              key={channel.title}
              className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                <MessageCircle size={21} />
              </div>

              <h3 className="mt-5 font-heading text-xl font-semibold text-luxury-ink">
                {channel.title}
              </h3>

              <p className="mt-3 text-sm leading-7 text-slate-600">
                {channel.description}
              </p>

              <Button asChild variant="outline" className="mt-6">
                <a href={channel.href}>
                  Continue
                  <ArrowRight className="ml-2" size={17} />
                </a>
              </Button>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
