import { BrandMark } from "@/components/brand/brand-mark";
import { AuthSidePanel } from "@/features/auth/components/auth-side-panel";

type AuthShellProps = {
  children: React.ReactNode;
  title: string;
  description: string;
};

export function AuthShell({ children, title, description }: AuthShellProps) {
  return (
    <main className="min-h-screen bg-luxury-gradient">
      <div className="nexivo-container flex min-h-screen items-center justify-center py-10">
        <div className="grid w-full max-w-6xl gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <AuthSidePanel />

          <section className="rounded-4xl border border-white/70 bg-white/90 p-6 shadow-premium backdrop-blur-xl md:p-10">
            <a href="/" className="inline-flex">
              <BrandMark />
            </a>

            <div className="mt-10">
              <h1 className="font-heading text-3xl font-semibold tracking-tight text-luxury-ink md:text-4xl">
                {title}
              </h1>
              <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
            </div>

            <div className="mt-8">{children}</div>
          </section>
        </div>
      </div>
    </main>
  );
}
