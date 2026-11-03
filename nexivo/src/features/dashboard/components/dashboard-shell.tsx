"use client";

import { LogOut, Menu } from "lucide-react";
import { useState } from "react";
import { BrandMark } from "@/components/brand/brand-mark";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store/auth.store";
import { cn } from "@/lib/utils";

type DashboardShellProps = {
  children: React.ReactNode;
  title: string;
  description: string;
  navigation: readonly {
    label: string;
    href: string;
    icon: React.ElementType;
  }[];
  roleLabel: string;
};

export function DashboardShell({
  children,
  title,
  description,
  navigation,
  roleLabel
}: DashboardShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, logout } = useAuthStore();

  return (
    <main className="min-h-screen bg-luxury-mist">
      <div className="grid min-h-screen lg:grid-cols-[300px_1fr]">
        <aside
          className={cn(
            "fixed inset-y-0 left-0 z-[80] w-[300px] -translate-x-full border-r border-slate-200 bg-white p-5 shadow-premium transition-transform lg:static lg:translate-x-0 lg:shadow-none",
            mobileOpen && "translate-x-0"
          )}
        >
          <div className="flex items-center justify-between">
            <a href="/">
              <BrandMark />
            </a>

            <button
              type="button"
              className="rounded-full p-2 text-slate-500 lg:hidden"
              onClick={() => setMobileOpen(false)}
            >
              ×
            </button>
          </div>

          <div className="mt-8 rounded-4xl bg-luxury-gradient p-5">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-luxury-gold">
              {roleLabel}
            </p>
            <h2 className="mt-3 font-heading text-lg font-semibold text-luxury-ink">
              {user?.fullName ?? "Nexivo User"}
            </h2>
            <p className="mt-1 text-sm text-slate-600">{user?.email ?? "user@nexivo.com"}</p>
          </div>

          <nav className="mt-6 space-y-2">
            {navigation.map((item) => {
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

          <div className="mt-8">
            <Button
              variant="outline"
              fullWidth
              onClick={async () => {
                await fetch("/api/auth/session", { method: "DELETE" });
                logout();
                window.location.href = "/";
              }}
            >
              <LogOut className="mr-2" size={17} />
              Logout
            </Button>
          </div>
        </aside>

        <section className="min-w-0">
          <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/85 backdrop-blur-xl">
            <div className="flex h-20 items-center justify-between px-5 md:px-8">
              <div>
                <p className="text-sm font-semibold text-brand-700">{roleLabel}</p>
                <h1 className="font-heading text-2xl font-semibold tracking-tight text-luxury-ink">
                  {title}
                </h1>
              </div>

              <button
                type="button"
                className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-slate-200 bg-white shadow-soft lg:hidden"
                onClick={() => setMobileOpen(true)}
              >
                <Menu size={20} />
              </button>
            </div>
          </header>

          <div className="px-5 py-8 md:px-8">
            <p className="mb-8 max-w-3xl text-sm leading-6 text-slate-600">{description}</p>
            {children}
          </div>
        </section>
      </div>
    </main>
  );
}
