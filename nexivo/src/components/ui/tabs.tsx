"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type TabItem = {
  value: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
};

type TabsProps = {
  items: TabItem[];
  value?: string;
  defaultValue?: string;
  onValueChange?: (value: string) => void;
  variant?: "default" | "pill" | "underline" | "premium";
  className?: string;
};

export function Tabs({
  items,
  value,
  defaultValue,
  onValueChange,
  variant = "default",
  className
}: TabsProps) {
  const [internalValue, setInternalValue] = React.useState(defaultValue ?? items[0]?.value);
  const selectedValue = value ?? internalValue;

  const updateValue = (nextValue: string) => {
    setInternalValue(nextValue);
    onValueChange?.(nextValue);
  };

  const variantClass = {
    default: "rounded-3xl border border-slate-200 bg-white p-1 shadow-soft",
    pill: "rounded-full bg-slate-100 p-1",
    underline: "border-b border-slate-200",
    premium: "rounded-4xl border border-white/70 bg-white/80 p-2 shadow-premium backdrop-blur-xl"
  }[variant];

  return (
    <div className={cn("flex flex-wrap gap-1", variantClass, className)} role="tablist">
      {items.map((item) => {
        const active = selectedValue === item.value;

        return (
          <button
            key={item.value}
            type="button"
            role="tab"
            aria-selected={active}
            disabled={item.disabled}
            onClick={() => updateValue(item.value)}
            className={cn(
              "inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-sm font-semibold transition-all disabled:pointer-events-none disabled:opacity-50",
              active
                ? "bg-luxury-ink text-white shadow-soft"
                : "text-slate-600 hover:bg-white hover:text-luxury-ink",
              variant === "underline" &&
                "rounded-none border-b-2 border-transparent bg-transparent shadow-none",
              variant === "underline" && active && "border-primary bg-transparent text-primary"
            )}
          >
            {item.icon}
            {item.label}
          </button>
        );
      })}
    </div>
  );
}
