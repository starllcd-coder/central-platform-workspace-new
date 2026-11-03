import type {
  PartnerBooking,
  PartnerInvoice,
  PartnerListing,
  PartnerStaff,
  PartnerSupportTicket
} from "@/features/partner/types/partner.types";

export const partnerListings: PartnerListing[] = [];
export const partnerBookings: PartnerBooking[] = [];
export const partnerInvoices: PartnerInvoice[] = [];
export const partnerStaff: PartnerStaff[] = [];
export const partnerSupportTickets: PartnerSupportTicket[] = [];

export const partnerReportMetrics = [
  { label: "Marketplace Views", value: "0", description: "Combined listing views." },
  { label: "Bookings", value: "0", description: "Confirmed and pending marketplace bookings." },
  { label: "Estimated Revenue", value: "0 OMR", description: "Gross booking value before fees." },
  { label: "Conversion Rate", value: "0%", description: "Marketplace visitor to booking conversion." }
] as const;
