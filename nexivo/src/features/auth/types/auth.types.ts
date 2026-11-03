export type AuthRole = "customer" | "partner" | "admin" | "staff";

export type AuthUser = {
  id: string;
  fullName: string;
  email: string;
  phone?: string;
  role: AuthRole;
  preferredLanguage: string;
  preferredCurrency: string;
  country?: string;
  timezone?: string;
};

export type AuthMode = "login" | "register" | "forgot-password";
