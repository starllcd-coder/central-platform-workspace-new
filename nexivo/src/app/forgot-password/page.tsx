import { AuthShell } from "@/features/auth/components/auth-shell";
import { ForgotPasswordForm } from "@/features/auth/components/forgot-password-form";

export default function ForgotPasswordPage() {
  return (
    <AuthShell
      title="Reset your password."
      description="Enter your email and we will prepare a secure reset flow for your Nexivo account."
    >
      <ForgotPasswordForm />
    </AuthShell>
  );
}
