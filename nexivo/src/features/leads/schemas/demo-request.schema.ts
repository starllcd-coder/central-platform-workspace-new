import { z } from "zod";

export const demoRequestSchema = z.object({
  fullName: z.string().min(2, "Enter your full name."),
  businessName: z.string().min(2, "Enter your business name."),
  email: z.string().email("Enter a valid email address."),
  phone: z.string().min(6, "Enter phone number."),
  country: z.string().min(2, "Select country."),
  city: z.string().min(2, "Enter city."),
  productInterest: z.enum(["staylux", "drivesphere", "laundrex", "central-platform", "multiple"]),
  businessType: z.string().min(2, "Enter business type."),
  estimatedSize: z.string().min(1, "Select business size."),
  message: z.string().optional()
});

export type DemoRequestInput = z.infer<typeof demoRequestSchema>;
