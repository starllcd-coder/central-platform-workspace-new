import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { FaqAccordionList } from "@/features/support/components/faq-accordion-list";
import { ContactChannelsGrid } from "@/features/support/components/contact-channels-grid";

export default function SupportPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="Support"
        title="Support for customers and businesses."
        description="Get help with bookings, payments, business demos, partner onboarding, and account settings."
      />

      <ContactChannelsGrid />
      <FaqAccordionList />
    </PublicPageLayout>
  );
}
