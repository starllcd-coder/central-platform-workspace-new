"use client";

import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

type DrawerProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  side?: "left" | "right" | "bottom";
  width?: "sm" | "md" | "lg";
};

export function Drawer({
  open,
  onOpenChange,
  title,
  description,
  children,
  side = "right",
  width = "md"
}: DrawerProps) {
  React.useEffect(() => {
    if (!open) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") onOpenChange(false);
    };

    document.addEventListener("keydown", handleEscape);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "";
    };
  }, [open, onOpenChange]);

  if (!open) return null;

  const widthClass = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-xl"
  }[width];

  const positionClass = {
    right: "right-0 top-0 h-full rounded-l-4xl",
    left: "left-0 top-0 h-full rounded-r-4xl",
    bottom: "bottom-0 left-0 right-0 max-h-[88vh] rounded-t-4xl"
  }[side];

  return (
    <div className="fixed inset-0 z-[90]">
      <button
        aria-label="Close drawer overlay"
        className="absolute inset-0 bg-luxury-ink/55 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />

      <aside
        className={cn(
          "absolute w-full overflow-hidden border border-white/70 bg-white shadow-premium",
          side === "bottom" ? "" : widthClass,
          positionClass
        )}
      >
        <div className="flex items-start justify-between gap-6 border-b border-slate-200 px-6 py-5">
          <div>
            {title ? (
              <h2 className="font-heading text-xl font-semibold text-luxury-ink">
                {title}
              </h2>
            ) : null}

            {description ? (
              <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
            ) : null}
          </div>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onOpenChange(false)}
            aria-label="Close drawer"
          >
            <X size={18} />
          </Button>
        </div>

        <div className="h-full max-h-[calc(100vh-86px)] overflow-y-auto px-6 py-6">
          {children}
        </div>
      </aside>
    </div>
  );
}
