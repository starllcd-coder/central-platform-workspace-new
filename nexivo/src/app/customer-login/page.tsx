import { AuthShell } from "@/features/auth/components/auth-shell";
import { LoginForm } from "@/features/auth/components/login-form";

export default function CustomerLoginPage() {
  return (
    <AuthShell
      title="Customer login."
      description="Access your Nexivo bookings, favorites, rewards, documents, reviews, and notifications."
    >
      <LoginForm mode="customer" />
    </AuthShell>
  );
}
