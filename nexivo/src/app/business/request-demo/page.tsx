import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { DemoRequestForm } from "@/features/leads/components/demo-request-form";
import { DemoRequestSidePanel } from "@/features/leads/components/demo-request-side-panel";

export default function RequestDemoPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Request Demo"
        title="Request a DSS product demo."
        description="Tell us about your business and the DSS product you are interested in. Nexivo will prepare a custom proposal after the demo discussion."
        spacing="compact"
      />

      <section className="bg-luxury-mist pb-16 pt-8 md:pb-20 md:pt-10">
        <div className="nexivo-container grid gap-8 lg:grid-cols-[1fr_420px]">
          <DemoRequestForm />
          <DemoRequestSidePanel />
        </div>
      </section>
    </PublicPageLayout>
  );
}
