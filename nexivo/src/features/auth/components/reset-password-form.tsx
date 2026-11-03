"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/forms/form-field";

export function ResetPasswordForm({ uid, token }: { uid: string; token: string }) {
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState("");
  const [done, setDone] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const password = String(data.get("password") || "");
    if (password !== data.get("confirmPassword")) { setMessage("Passwords do not match."); return; }
    setPending(true);
    setMessage("");
    try {
      const response = await fetch("/api/auth/password-reset/confirm", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ uid, token, password })
      });
      const result = await response.json();
      if (response.ok) { setDone(true); setMessage(result.data.detail); }
      else { setMessage(result.error?.message || "This reset link is invalid or expired."); }
    } catch { setMessage("Password recovery is unavailable. Please try again."); }
    finally { setPending(false); }
  }
  return (
    <form onSubmit={submit} className="space-y-5">
      {!done ? <>
        <FormField label="New password">
          <Input name="password" type="password" minLength={8} required autoComplete="new-password" />
        </FormField>
        <FormField label="Confirm new password">
          <Input name="confirmPassword" type="password" minLength={8} required autoComplete="new-password" />
        </FormField>
        <Button type="submit" disabled={pending || !uid || !token} variant="luxury" size="lg" fullWidth>
          {pending ? "Updating..." : "Update Password"}
        </Button>
      </> : null}
      {message ? <p role="status" className="text-sm text-slate-600">{message}</p> : null}
      <p className="text-center text-sm text-slate-600">
        <a href={done ? "/login" : "/forgot-password"} className="font-semibold text-brand-700 hover:underline">
          {done ? "Sign in" : "Request another reset link"}
        </a>
      </p>
    </form>
  );
}
