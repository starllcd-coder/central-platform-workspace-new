import { AuthShell } from "@/features/auth/components/auth-shell";
import { RegisterForm } from "@/features/auth/components/register-form";

export default function RegisterPage() {
  return (
    <AuthShell
      title="Create your Nexivo account."
      description="Register once and use the same account for stays, cars, laundry, rewards, reviews, and future services."
    >
      <RegisterForm />
    </AuthShell>
  );
}
