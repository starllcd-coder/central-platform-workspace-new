import { pricingFaqs } from "@/features/pricing/data/pricing-data";
import { SectionHeading } from "@/components/layout/section-heading";
import { SectionShell } from "@/components/layout/section-shell";

export function PricingFaqSection() {
  return (
    <SectionShell background="default">
      <SectionHeading
        eyebrow="Pricing Questions"
        title="Keep pricing clear, but not restrictive."
        description="Nexivo pricing should be transparent enough to attract businesses, while flexible enough for future commercial adjustment."
        align="center"
      />

      <div className="mx-auto mt-10 max-w-4xl space-y-4">
        {pricingFaqs.map((faq) => (
          <article
            key={faq.question}
            className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft"
          >
            <h3 className="font-heading text-xl font-semibold text-luxury-ink">
              {faq.question}
            </h3>
            <p className="mt-3 text-sm leading-7 text-slate-600">{faq.answer}</p>
          </article>
        ))}
      </div>
    </SectionShell>
  );
}
