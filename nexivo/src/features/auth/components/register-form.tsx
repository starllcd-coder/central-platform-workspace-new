"use client";

import { Eye, EyeOff, Lock, Mail, Phone, UserRound } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { FormField } from "@/components/forms/form-field";
import { currencyOptions, localeOptions } from "@/config/localization-options";
import { phoneCountryCodes } from "@/features/auth/data/auth-options";
import { useAuthStore } from "@/features/auth/store/auth.store";
import type { AuthUser } from "@/features/auth/types/auth.types";

type RegisterResponse = {
  success: boolean;
  data?: {
    user: AuthUser;
  };
};

export function RegisterForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState<"idle" | "submitting" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("Central Platform could not create this account.");
  const setAuthenticatedUser = useAuthStore((state) => state.setAuthenticatedUser);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("submitting");

    const form = new FormData(event.currentTarget);
    const password = String(form.get("password") ?? "");
    const confirmPassword = String(form.get("confirmPassword") ?? "");

    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match.");
      setStatus("error");
      return;
    }

    const accountType = String(form.get("accountType") ?? "customer");
    if (accountType === "business") {
      window.location.href = "/business/request-demo";
      return;
    }
    const body = {
      fullName: String(form.get("fullName") ?? ""),
      email: String(form.get("email") ?? ""),
      password,
      phone: `${String(form.get("phoneCode") ?? "")}${String(form.get("phone") ?? "")}`,
      accountType: "customer",
      preferredLanguage: String(form.get("preferredLanguage") ?? "en"),
      preferredCurrency: String(form.get("preferredCurrency") ?? "OMR")
    };

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const payload = (await response.json()) as RegisterResponse;

      if (!response.ok || !payload.success || !payload.data) {
        throw new Error("Registration failed");
      }

      setAuthenticatedUser(payload.data.user);
      window.location.href = "/verify-email";
    } catch {
      setErrorMessage("Central Platform could not create this account.");
      setStatus("error");
    }
  }

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      <div className="grid gap-5 md:grid-cols-2">
        <FormField label="Full name">
          <Input
            name="fullName"
            placeholder="Your full name"
            leftIcon={<UserRound size={17} />}
            autoComplete="name"
            required
          />
        </FormField>

        <FormField label="Email address">
          <Input
            name="email"
            type="email"
            placeholder="you@example.com"
            leftIcon={<Mail size={17} />}
            autoComplete="email"
            required
          />
        </FormField>
      </div>

      <div className="grid gap-5 md:grid-cols-[0.45fr_1fr]">
        <FormField label="Code">
          <Select name="phoneCode" defaultValue="+968">
            {phoneCountryCodes.map((item) => (
              <option key={item.code} value={item.code}>
                {item.code} {item.country}
              </option>
            ))}
          </Select>
        </FormField>

        <FormField label="Phone number">
          <Input
            name="phone"
            placeholder="Phone number"
            leftIcon={<Phone size={17} />}
            autoComplete="tel"
          />
        </FormField>
      </div>

      <div className="grid gap-5 md:grid-cols-3">
        <FormField label="Account type">
          <Select name="accountType" defaultValue="customer">
            <option value="customer">Customer</option>
            <option value="business">Business / Partner</option>
          </Select>
        </FormField>

        <FormField label="Language">
          <Select name="preferredLanguage" defaultValue="en">
            {localeOptions.map((item) => (
              <option key={item.code} value={item.code}>
                {item.nativeLabel}
              </option>
            ))}
          </Select>
        </FormField>

        <FormField label="Currency">
          <Select name="preferredCurrency" defaultValue="OMR">
            {currencyOptions.map((item) => (
              <option key={item.code} value={item.code}>
                {item.code} - {item.label}
              </option>
            ))}
          </Select>
        </FormField>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <FormField label="Password">
          <Input
            name="password"
            type={showPassword ? "text" : "password"}
            placeholder="Create password"
            leftIcon={<Lock size={17} />}
            rightIcon={
              <button
                type="button"
                onClick={() => setShowPassword((value) => !value)}
                className="text-slate-400 hover:text-slate-700"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
              </button>
            }
            autoComplete="new-password"
            required
          />
        </FormField>

        <FormField label="Confirm password">
          <Input
            name="confirmPassword"
            type={showPassword ? "text" : "password"}
            placeholder="Confirm password"
            leftIcon={<Lock size={17} />}
            autoComplete="new-password"
            required
          />
        </FormField>
      </div>

      <div className="space-y-3 rounded-3xl border border-slate-200 bg-slate-50 p-4">
        <label className="flex gap-3 text-sm leading-6 text-slate-600">
          <input
            name="termsAccepted"
            type="checkbox"
            required
            className="mt-1 h-4 w-4 rounded border-slate-300 text-brand-600"
          />
          <span>I agree to Nexivo Terms of Service and Privacy Policy.</span>
        </label>

        <label className="flex gap-3 text-sm leading-6 text-slate-600">
          <input name="marketingAccepted" type="checkbox" className="mt-1 h-4 w-4 rounded border-slate-300 text-brand-600" />
          <span>I agree to receive booking updates, offers, and service notifications.</span>
        </label>
      </div>

      {status === "error" ? (
        <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {errorMessage}
        </p>
      ) : null}

      <Button type="submit" variant="luxury" size="lg" fullWidth disabled={status === "submitting"}>
        {status === "submitting" ? "Creating..." : "Create Nexivo Account"}
      </Button>

      <p className="text-center text-sm text-slate-600">
        Already have an account?{" "}
        <a href="/login" className="font-semibold text-brand-700 hover:underline">
          Login
        </a>
      </p>
    </form>
  );
}
