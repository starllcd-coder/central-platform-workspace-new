import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";

export default function TermsPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Terms"
        title="Nexivo terms and platform rules."
        description="Placeholder terms page prepared for legal review before accepting real bookings, payments, partner registrations, and customer accounts."
      />

      <section className="section-padding bg-luxury-mist">
        <div className="nexivo-container">
          <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-premium">
            <h2 className="font-heading text-2xl font-semibold text-luxury-ink">
              Legal review required
            </h2>
            <p className="mt-4 text-sm leading-7 text-slate-600">
              Before production launch, replace this placeholder with reviewed Terms of Service,
              booking policies, cancellation rules, payment terms, partner agreement references,
              privacy references, dispute handling, refund rules, and jurisdiction details.
            </p>
          </div>
        </div>
      </section>
    </PublicPageLayout>
  );
}
