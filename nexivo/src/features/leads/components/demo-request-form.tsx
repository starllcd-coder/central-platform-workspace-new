"use client";

import { type FormEvent, useRef, useState } from "react";
import { Building2, Mail, MapPin, Phone, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  businessSizeOptions,
  businessTypeOptions,
  productInterestOptions
} from "@/features/leads/data/lead-options";
import { countries } from "@/features/geo/data/countries";
import { demoRequestSchema } from "@/features/leads/schemas/demo-request.schema";

export function DemoRequestForm() {
  const idempotencyKey = useRef(crypto.randomUUID());
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const values = Object.fromEntries(new FormData(form).entries());
    const parsed = demoRequestSchema.safeParse(values);
    if (!parsed.success) {
      setStatus("error");
      setMessage(parsed.error.issues[0]?.message ?? "Check the form and try again.");
      return;
    }

    setStatus("submitting");
    setMessage("");
    try {
      const response = await fetch("/api/leads/demo-request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey.current
        },
        body: JSON.stringify(parsed.data)
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.error?.message ?? "Unable to submit the demo request.");
      }
      form.reset();
      idempotencyKey.current = crypto.randomUUID();
      setStatus("success");
      setMessage("Your demo request was submitted and is awaiting Central Platform approval.");
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Unable to submit the demo request.");
    }
  }

  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Request a DSS product demo</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Submit your business details for Central Platform review and approval.
        </p>
      </CardHeader>

      <CardContent>
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="grid gap-5 md:grid-cols-2">
            <FormField label="Full name">
              <Input name="fullName" required placeholder="Your full name" leftIcon={<UserRound size={17} />} />
            </FormField>
            <FormField label="Business name">
              <Input name="businessName" required placeholder="Business name" leftIcon={<Building2 size={17} />} />
            </FormField>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <FormField label="Email">
              <Input name="email" required type="email" placeholder="you@business.com" leftIcon={<Mail size={17} />} />
            </FormField>
            <FormField label="Phone">
              <Input name="phone" required placeholder="+968..." leftIcon={<Phone size={17} />} />
            </FormField>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <FormField label="Country">
              <Select name="country" required defaultValue="OM">
                {countries.map((country) => (
                  <option key={country.code} value={country.code}>
                    {country.name}
                  </option>
                ))}
              </Select>
            </FormField>
            <FormField label="City">
              <Input name="city" required placeholder="City" leftIcon={<MapPin size={17} />} />
            </FormField>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <FormField label="Product interest">
              <Select name="productInterest" required defaultValue="staylux">
                {productInterestOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
            </FormField>
            <FormField label="Business size">
              <Select name="estimatedSize" required defaultValue="small">
                {businessSizeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
            </FormField>
          </div>

          <FormField label="Business type">
            <Select name="businessType" required defaultValue="Hotel">
              {businessTypeOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </Select>
          </FormField>

          <FormField label="Message">
            <Textarea
              name="message"
              placeholder="Tell us about your business, number of rooms/vehicles/orders, and what you want to achieve with Nexivo."
              className="min-h-36"
            />
          </FormField>

          <Button type="submit" disabled={status === "submitting"} variant="luxury" size="lg" fullWidth>
            {status === "submitting" ? "Submitting..." : "Submit Demo Request"}
          </Button>
          {message ? (
            <p
              className={status === "success" ? "text-sm text-emerald-700" : "text-sm text-red-700"}
              role={status === "error" ? "alert" : "status"}
              aria-live="polite"
            >
              {message}
            </p>
          ) : null}
        </form>
      </CardContent>
    </Card>
  );
}
