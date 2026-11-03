export type PartnerProduct = "staylux" | "drivesphere" | "laundrex";

export type PartnerListingStatus = "active" | "pending" | "paused" | "draft";

export type PartnerListing = {
  id: string;
  product: PartnerProduct;
  title: string;
  location: string;
  status: PartnerListingStatus;
  views: number;
  bookings: number;
  revenue: string;
};

export type PartnerBooking = {
  id: string;
  product: PartnerProduct;
  customer: string;
  service: string;
  date: string;
  amount: string;
  status: "confirmed" | "pending" | "completed" | "cancelled";
};

export type PartnerInvoice = {
  id: string;
  title: string;
  amount: string;
  dueDate: string;
  status: "paid" | "unpaid" | "overdue";
};

export type PartnerStaff = {
  id: string;
  name: string;
  email: string;
  role: string;
  productAccess: PartnerProduct[];
  status: "active" | "invited" | "disabled";
};

export type PartnerSupportTicket = {
  id: string;
  subject: string;
  category: "billing" | "technical" | "booking" | "onboarding";
  status: "open" | "in-progress" | "resolved";
  createdAt: string;
};
