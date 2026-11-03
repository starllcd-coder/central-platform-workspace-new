import { HelpCircle } from "lucide-react";
import { supportFaqs } from "@/features/support/data/support-data";

export function FaqAccordionList() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="mx-auto max-w-4xl space-y-4">
          {supportFaqs.map((faq) => (
            <article
              key={faq.question}
              className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft"
            >
              <div className="flex gap-4">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand-50 text-brand-700">
                  <HelpCircle size={20} />
                </div>

                <div>
                  <h3 className="font-heading text-xl font-semibold text-luxury-ink">
                    {faq.question}
                  </h3>
                  <p className="mt-3 text-sm leading-7 text-slate-600">{faq.answer}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
