import { AuthShell } from "@/features/auth/components/auth-shell";
import { LoginForm } from "@/features/auth/components/login-form";

export default function PartnerLoginPage() {
  return (
    <AuthShell
      title="Partner login."
      description="Access your Nexivo Partner Portal for StayLux, DriveSphere, Laundrex, billing, reports, and support."
    >
      <LoginForm mode="partner" />
    </AuthShell>
  );
}
