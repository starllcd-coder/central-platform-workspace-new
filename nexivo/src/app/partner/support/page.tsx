import { PartnerSupportList } from "@/features/partner/components/partner-support-list";
import { partnerSupportTickets } from "@/features/partner/data/partner-dashboard-data";

export default function PartnerSupportPage() {
  return <PartnerSupportList tickets={partnerSupportTickets} />;
}
