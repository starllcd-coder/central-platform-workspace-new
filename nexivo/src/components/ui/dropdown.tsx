"use client";

import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

type DropdownItem = {
  label: string;
  value: string;
  description?: string;
  icon?: React.ReactNode;
  disabled?: boolean;
};

type DropdownProps = {
  label: string;
  items: DropdownItem[];
  value?: string;
  onChange?: (value: string) => void;
  align?: "left" | "right";
  className?: string;
};

export function Dropdown({
  label,
  items,
  value,
  onChange,
  align = "left",
  className
}: DropdownProps) {
  const [open, setOpen] = React.useState(false);
  const selected = items.find((item) => item.value === value);

  React.useEffect(() => {
    if (!open) return;

    const close = () => setOpen(false);
    window.addEventListener("click", close);

    return () => window.removeEventListener("click", close);
  }, [open]);

  return (
    <div className={cn("relative inline-block", className)} onClick={(event) => event.stopPropagation()}>
      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        className="inline-flex h-11 items-center gap-2 rounded-full border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 shadow-soft"
      >
        {selected?.icon}
        {selected?.label ?? label}
        <ChevronDown size={15} />
      </button>

      {open ? (
        <div
          className={cn(
            "absolute top-13 z-50 w-72 rounded-3xl border border-slate-200 bg-white p-2 shadow-premium",
            align === "right" ? "right-0" : "left-0"
          )}
        >
          {items.map((item) => (
            <button
              key={item.value}
              type="button"
              disabled={item.disabled}
              onClick={() => {
                onChange?.(item.value);
                setOpen(false);
              }}
              className={cn(
                "flex w-full items-start gap-3 rounded-2xl px-4 py-3 text-left text-sm transition-colors hover:bg-slate-50 disabled:pointer-events-none disabled:opacity-50",
                item.value === value && "bg-brand-50"
              )}
            >
              {item.icon ? (
                <span className="mt-0.5 text-brand-700">{item.icon}</span>
              ) : null}

              <span>
                <span className="block font-semibold text-slate-800">{item.label}</span>
                {item.description ? (
                  <span className="mt-1 block text-xs leading-5 text-slate-500">
                    {item.description}
                  </span>
                ) : null}
              </span>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
