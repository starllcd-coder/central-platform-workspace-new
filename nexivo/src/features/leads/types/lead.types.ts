export type LeadSource = "website" | "pricing" | "business-page" | "product-page";

export type DemoRequestLead = {
  id: string;
  fullName: string;
  businessName: string;
  email: string;
  phone: string;
  country: string;
  city: string;
  productInterest: "staylux" | "drivesphere" | "laundrex" | "central-platform" | "multiple";
  businessType: string;
  estimatedSize: string;
  message?: string;
  source: LeadSource;
  status: "new" | "contacted" | "demo-scheduled" | "proposal-sent" | "closed";
  createdAt: string;
};
