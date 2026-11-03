export type CentralPlatformModule =
  | "identity"
  | "tenants"
  | "marketplace"
  | "pricing"
  | "payments"
  | "billing"
  | "notifications"
  | "analytics"
  | "privacy"
  | "integrations";

export type IntegrationStatus = "connected" | "mock" | "planned" | "error";

export type IntegrationConnector = {
  id: string;
  name: string;
  module: CentralPlatformModule;
  description: string;
  status: IntegrationStatus;
  endpoint: string;
  requiredForLaunch: boolean;
};

export type CentralSyncPayload = {
  entity:
    | "stays"
    | "cars"
    | "laundry"
    | "customers"
    | "partners"
    | "bookings"
    | "pricing"
    | "leads";
  action: "pull" | "push" | "sync";
  records: number;
};
