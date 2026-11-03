import {
  Activity,
  BarChart3,
  FileBarChart,
  FileClock,
  LayoutDashboard,
  LogOut
} from "lucide-react";
import { BrandMark } from "@/components/brand/brand-mark";

const adminNavigation = [
  { label: "Overview", href: "/admin", icon: LayoutDashboard },
  { label: "Analytics", href: "/admin/analytics", icon: BarChart3 },
  { label: "Monitoring", href: "/admin/monitoring", icon: Activity },
  { label: "Audit Logs", href: "/admin/audit-logs", icon: FileClock },
  { label: "Reports", href: "/admin/reports", icon: FileBarChart }
] as const;

export default function AdminLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="min-h-screen bg-luxury-mist">
      <div className="grid min-h-screen lg:grid-cols-[300px_1fr]">
        <aside className="hidden border-r border-slate-200 bg-white p-5 lg:block">
          <a href="/">
            <BrandMark />
          </a>

          <div className="mt-8 rounded-4xl bg-midnight-gradient p-5 text-white">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-luxury-gold">
              Admin Console
            </p>
            <h2 className="mt-3 font-heading text-lg font-semibold">Nexivo Monitoring</h2>
            <p className="mt-1 text-sm text-white/65">DSS Central Platform readiness</p>
          </div>

          <nav className="mt-6 space-y-2">
            {adminNavigation.map((item) => {
              const Icon = item.icon;

              return (
                <a
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 rounded-3xl px-4 py-3 text-sm font-semibold text-slate-700 transition-colors hover:bg-brand-50 hover:text-brand-700"
                >
                  <Icon size={18} />
                  {item.label}
                </a>
              );
            })}
          </nav>

          <a
            href="/"
            className="mt-8 flex items-center justify-center gap-2 rounded-3xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700"
          >
            <LogOut size={17} />
            Exit Admin
          </a>
        </aside>

        <section className="min-w-0">
          <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/85 backdrop-blur-xl">
            <div className="flex h-20 items-center justify-between px-5 md:px-8">
              <div>
                <p className="text-sm font-semibold text-brand-700">Admin Console</p>
                <h1 className="font-heading text-2xl font-semibold tracking-tight text-luxury-ink">
                  Analytics, Monitoring & Audit
                </h1>
              </div>

              <a
                href="/"
                className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold shadow-soft lg:hidden"
              >
                Home
              </a>
            </div>
          </header>

          <div className="px-5 py-8 md:px-8">{children}</div>
        </section>
      </div>
    </main>
  );
}
