import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { ContactChannelsGrid } from "@/features/support/components/contact-channels-grid";

export default function ContactPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Contact"
        title="Contact Nexivo and DSS."
        description="Choose the correct contact path for business demos, customer support, or partner access."
      />

      <ContactChannelsGrid />
    </PublicPageLayout>
  );
}
