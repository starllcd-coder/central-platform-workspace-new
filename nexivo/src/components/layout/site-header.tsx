"use client";

import { Menu, X } from "lucide-react";
import { useState } from "react";
import { BrandMark } from "@/components/brand/brand-mark";
import { HeaderControls } from "@/components/navigation/header-controls";
import { Button } from "@/components/ui/button";
import { mainNavigation } from "@/config/navigation";
import { cn } from "@/lib/utils";

export function SiteHeader() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-[100] border-b border-luxury-dune/60 bg-white/90 backdrop-blur-xl">
      <div className="nexivo-container">
        <div className="flex h-20 items-center justify-between gap-4">
          <a href="/" aria-label="Nexivo Home" className="shrink-0">
            <BrandMark />
          </a>

          <nav aria-label="Main navigation" className="hidden items-center gap-1 lg:flex">
            {mainNavigation.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="rounded-full px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-brand-50 hover:text-brand-700"
              >
                {item.label}
              </a>
            ))}
          </nav>

          <div className="hidden items-center gap-3 lg:flex">
            <HeaderControls />
            <Button asChild variant="outline" size="md">
              <a href="/login">Login</a>
            </Button>
            <Button asChild variant="luxury" size="md">
              <a href="/business/request-demo">Request Demo</a>
            </Button>
          </div>

          <button
            type="button"
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
            onClick={() => setOpen((value) => !value)}
            className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-slate-200 bg-white shadow-soft lg:hidden"
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      <div
        className={cn(
          "grid border-t border-slate-200 bg-white transition-all duration-300 lg:hidden",
          open ? "grid-rows-[1fr]" : "grid-rows-[0fr]"
        )}
      >
        <div className="overflow-hidden">
          <div className="nexivo-container py-5">
            <nav aria-label="Mobile navigation" className="grid gap-2">
              {mainNavigation.map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className="rounded-3xl px-4 py-3 text-sm font-semibold text-slate-700 hover:bg-brand-50 hover:text-brand-700"
                >
                  {item.label}
                </a>
              ))}
            </nav>

            <div className="mt-5 flex flex-col gap-3">
              <HeaderControls />
              <Button asChild variant="outline" fullWidth>
                <a href="/login">Login</a>
              </Button>
              <Button asChild variant="luxury" fullWidth>
                <a href="/business/request-demo">Request Demo</a>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
