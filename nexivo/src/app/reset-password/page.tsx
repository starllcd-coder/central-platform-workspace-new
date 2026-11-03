import { AuthShell } from "@/features/auth/components/auth-shell";
import { ResetPasswordForm } from "@/features/auth/components/reset-password-form";

export default async function ResetPasswordPage({ searchParams }: {
  searchParams: Promise<{ uid?: string; token?: string }>;
}) {
  const params = await searchParams;
  return (
    <AuthShell title="Choose a new password." description="Set a new password for your Nexivo account.">
      <ResetPasswordForm uid={params.uid || ""} token={params.token || ""} />
    </AuthShell>
  );
}
