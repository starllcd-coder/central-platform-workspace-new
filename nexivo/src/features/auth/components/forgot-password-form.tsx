"use client";

import { useState, type FormEvent } from "react";
﻿import { Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/forms/form-field";

export function ForgotPasswordForm() {
  const [message, setMessage] = useState("");
  const [pending, setPending] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const email = String(new FormData(event.currentTarget).get("email") || "");
    setPending(true);
    setMessage("");
    try {
      const response = await fetch("/api/auth/password-reset", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email })
      });
      const result = await response.json();
      setMessage(response.ok ? result.data.detail : result.error?.message || "Password recovery is unavailable. Please try again.");
    } catch {
      setMessage("Password recovery is unavailable. Please try again.");
    } finally { setPending(false); }
  }
  return (
    <form onSubmit={submit} className="space-y-5">
      <FormField
        label="Email address"
        description="Enter the email connected with your Nexivo account."
      >
        <Input
          name="email"
          required
          type="email"
          placeholder="you@example.com"
          leftIcon={<Mail size={17} />}
          autoComplete="email"
        />
      </FormField>

      <Button type="submit" disabled={pending} variant="luxury" size="lg" fullWidth>
        {pending ? "Sending..." : "Send Reset Link"}
      </Button>

      {message ? <p role="status" className="text-sm text-slate-600">{message}</p> : null}

      <p className="text-center text-sm text-slate-600">
        Remembered your password?{" "}
        <a href="/login" className="font-semibold text-brand-700 hover:underline">
          Back to login
        </a>
      </p>
    </form>
  );
}
