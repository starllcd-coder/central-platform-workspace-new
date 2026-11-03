import { AuthShell } from "@/features/auth/components/auth-shell";
import { LoginForm } from "@/features/auth/components/login-form";

export default function LoginPage() {
  return (
    <AuthShell
      title="Welcome back to Nexivo."
      description="Login to manage your stays, car rentals, laundry orders, rewards, and saved preferences."
    >
      <LoginForm mode="customer" />
    </AuthShell>
  );
}
