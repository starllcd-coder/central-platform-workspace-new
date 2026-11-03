"use client";

import { motion, AnimatePresence } from "framer-motion";
import { mainNavigation, businessNavigation } from "@/config/navigation";
import { Button } from "@/components/ui/button";
import { HeaderControls } from "@/components/navigation/header-controls";

type MobileNavigationProps = {
  open: boolean;
  onClose: () => void;
};

export function MobileNavigation({ open, onClose }: MobileNavigationProps) {
  const allItems = [...mainNavigation, ...businessNavigation];

  return (
    <AnimatePresence>
      {open ? (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.22 }}
          className="border-t border-slate-200 bg-white px-5 py-5 shadow-premium lg:hidden"
        >
          <div className="mb-5 flex flex-wrap gap-3">
            <HeaderControls />
          </div>

          <nav className="grid gap-2" aria-label="Mobile navigation">
            {allItems.map((item) => {
              const Icon = item.icon;

              return (
                <a
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className="flex items-start gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft"
                >
                  <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand-50 text-brand-700">
                    <Icon size={20} />
                  </span>

                  <span>
                    <span className="block font-heading text-base font-semibold text-luxury-ink">
                      {item.label}
                    </span>
                    <span className="mt-1 block text-sm leading-5 text-slate-500">
                      {item.description}
                    </span>
                  </span>
                </a>
              );
            })}
          </nav>

          <div className="mt-5 grid gap-3">
            <Button asChild variant="outline" fullWidth>
              <a href="/login" onClick={onClose}>
                Login
              </a>
            </Button>

            <Button asChild variant="luxury" fullWidth>
              <a href="/business/request-demo" onClick={onClose}>
                Request Demo
              </a>
            </Button>
          </div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
