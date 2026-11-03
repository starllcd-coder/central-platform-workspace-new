export type ConsentCategory =
  | "strictly-necessary"
  | "analytics"
  | "marketing"
  | "personalization"
  | "third-party";

export type ConsentPreference = {
  category: ConsentCategory;
  title: string;
  description: string;
  required: boolean;
  enabled: boolean;
};

export type DataRequestType =
  | "access"
  | "export"
  | "delete"
  | "rectify"
  | "restrict-processing"
  | "withdraw-consent";

export type DataRequest = {
  id: string;
  type: DataRequestType;
  title: string;
  description: string;
  status: "draft" | "submitted" | "in-review" | "completed";
  createdAt: string;
};

export type SecurityControl = {
  id: string;
  title: string;
  description: string;
  area: "account" | "payments" | "business" | "data" | "compliance";
  status: "ready" | "planned";
};
