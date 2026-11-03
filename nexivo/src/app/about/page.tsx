import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";

export default function AboutPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="About Nexivo"
        title="A unified marketplace powered by Deedarian Software Solutions."
        description="Nexivo combines StayLux, DriveSphere, Laundrex, and DSS Central Platform into one GCC-first, Europe-ready customer and business ecosystem."
      />

      <SectionShell background="default">
        <div className="grid gap-8 lg:grid-cols-3">
          {[
            {
              title: "Customer marketplace",
              description:
                "Customers can search stays, cars, and laundry services from one modern platform."
            },
            {
              title: "Business software",
              description:
                "Businesses can use DSS products to manage operations and connect with Nexivo demand."
            },
            {
              title: "Central control",
              description:
                "Pricing, tenants, billing, integrations, analytics, and privacy should stay centralized."
            }
          ].map((item) => (
            <article
              key={item.title}
              className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft"
            >
              <h2 className="font-heading text-2xl font-semibold text-luxury-ink">
                {item.title}
              </h2>
              <p className="mt-3 text-sm leading-7 text-slate-600">{item.description}</p>
            </article>
          ))}
        </div>
      </SectionShell>

      <SectionShell background="muted">
        <CtaBand
          title="Build Nexivo as a premium travel-service ecosystem."
          description="The strongest strategy is one public customer marketplace and one powerful DSS business platform behind it."
          primaryLabel="Explore Marketplace"
          primaryHref="/stays"
          secondaryLabel="For Business"
          secondaryHref="/business"
        />
      </SectionShell>
    </PublicPageLayout>
  );
}
