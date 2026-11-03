import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(8, "Password must be at least 8 characters."),
  rememberMe: z.boolean().default(false)
});

export const registerSchema = z.object({
  fullName: z.string().min(2, "Enter your full name."),
  email: z.string().email("Enter a valid email address."),
  phoneCountryCode: z.string().min(2, "Select country code."),
  phoneNumber: z.string().min(6, "Enter your phone number."),
  customerType: z.enum(["customer", "business"]),
  preferredLanguage: z.string().min(2, "Select preferred language."),
  preferredCurrency: z.string().min(3, "Select preferred currency."),
  password: z.string().min(8, "Password must be at least 8 characters."),
  confirmPassword: z.string().min(8, "Confirm your password."),
  marketingConsent: z.boolean().default(false),
  termsAccepted: z.boolean().refine((value) => value === true, {
    message: "You must accept the terms."
  })
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match.",
  path: ["confirmPassword"]
});

export const forgotPasswordSchema = z.object({
  email: z.string().email("Enter a valid email address.")
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>;
