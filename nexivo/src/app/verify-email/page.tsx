import { CheckCircle2, Mail } from "lucide-react";
import { AuthShell } from "@/features/auth/components/auth-shell";
import { Button } from "@/components/ui/button";

export default function VerifyEmailPage() {
  return (
    <AuthShell
      title="Verify your email."
      description="Your Nexivo account is prepared. Email verification will secure your profile and booking access."
    >
      <div className="rounded-4xl border border-slate-200 bg-slate-50 p-6 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
          <Mail size={28} />
        </div>

        <h2 className="mt-5 font-heading text-2xl font-semibold text-luxury-ink">
          Check your inbox
        </h2>

        <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-slate-600">
          We will send a verification link to your email. After verification, your Nexivo account can be used across booking, partner, and service workflows.
        </p>

        <div className="mt-6 flex items-center justify-center gap-2 text-sm font-semibold text-emerald-700">
          <CheckCircle2 size={18} />
          Account preferences saved
        </div>

        <Button asChild variant="luxury" size="lg" fullWidth className="mt-6">
          <a href="/login">Continue to Login</a>
        </Button>
      </div>
    </AuthShell>
  );
}
