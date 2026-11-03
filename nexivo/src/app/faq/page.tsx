import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { PageHero } from "@/components/pages/page-hero";
import { FaqAccordionList } from "@/features/support/components/faq-accordion-list";

export default function FaqPage() {
  return (
    <PublicPageLayout>
      <PageHero
        eyebrow="FAQ"
        title="Frequently asked questions."
        description="Important questions about Nexivo booking, business pricing, commissions, GCC launch, and European expansion."
      />

      <FaqAccordionList />
    </PublicPageLayout>
  );
}
