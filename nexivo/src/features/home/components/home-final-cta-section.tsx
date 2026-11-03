import { CtaBand } from "@/components/marketing/cta-band";
import { SectionShell } from "@/components/layout/section-shell";

export function HomeFinalCtaSection() {
  return (
    <SectionShell background="default">
      <CtaBand
        title="Nexivo is built as a premium GCC marketplace with Europe-ready architecture."
        description="Customers see one elegant booking platform. Businesses get DSS-powered software, marketplace visibility, billing, pricing, reporting, and future expansion capability."
        primaryLabel="Start Booking"
        primaryHref="/stays"
        secondaryLabel="Join as Business"
        secondaryHref="/business"
      />
    </SectionShell>
  );
}
