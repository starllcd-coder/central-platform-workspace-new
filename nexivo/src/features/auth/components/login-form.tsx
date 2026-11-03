"use client";

import { Eye, EyeOff, Lock, Mail } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/forms/form-field";
import { useAuthStore } from "@/features/auth/store/auth.store";
import type { AuthUser } from "@/features/auth/types/auth.types";

type LoginFormProps = {
  mode?: "customer" | "partner";
};

type AuthResponse = {
  success: boolean;
  data?: {
    user: AuthUser;
  };
};

export function LoginForm({ mode = "customer" }: LoginFormProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState<"idle" | "submitting" | "error">("idle");
  const setAuthenticatedUser = useAuthStore((state) => state.setAuthenticatedUser);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("submitting");

    const form = new FormData(event.currentTarget);
    const endpoint = mode === "partner" ? "/api/auth/provider-login" : "/api/auth/login";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: String(form.get("email") ?? ""),
          password: String(form.get("password") ?? ""),
          otp: String(form.get("otp") ?? "")
        })
      });
      const payload = (await response.json()) as AuthResponse;

      if (!response.ok || !payload.success || !payload.data) {
        throw new Error("Login failed");
      }

      setAuthenticatedUser(payload.data.user);
      window.location.href = payload.data.user.role === "admin" ? "/admin" : mode === "partner" ? "/partner" : "/customer";
    } catch {
      setStatus("error");
    }
  }

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
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

      <FormField label="Password">
        <Input
          name="password"
          type={showPassword ? "text" : "password"}
          placeholder="Enter your password"
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
          autoComplete="current-password"
          required
        />
      </FormField>

      {mode === "partner" ? <FormField label="Authenticator code" description="Enter your code if two-factor authentication is enabled."><Input name="otp" inputMode="numeric" autoComplete="one-time-code" /></FormField> : null}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <label className="inline-flex items-center gap-2 text-sm font-medium text-slate-600">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
          />
          Remember me
        </label>

        <a href="/forgot-password" className="text-sm font-semibold text-brand-700 hover:underline">
          Forgot password?
        </a>
      </div>

      {status === "error" ? (
        <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Central Platform could not verify those credentials.
        </p>
      ) : null}

      <Button type="submit" variant="luxury" size="lg" fullWidth disabled={status === "submitting"}>
        {status === "submitting" ? "Checking..." : "Login"}
      </Button>

      <p className="text-center text-sm text-slate-600">
        Do not have an account?{" "}
        <a href="/register" className="font-semibold text-brand-700 hover:underline">
          Create account
        </a>
      </p>
    </form>
  );
}
