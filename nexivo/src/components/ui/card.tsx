import * as React from "react";
import { cn } from "@/lib/utils";

type CardProps = React.HTMLAttributes<HTMLDivElement> & {
  variant?: "default" | "premium" | "glass" | "dark" | "muted";
};

export function Card({ className, variant = "default", ...props }: CardProps) {
  const variants = {
    default: "rounded-3xl border border-slate-200 bg-white shadow-soft",
    premium: "rounded-4xl border border-white/70 bg-white/90 shadow-premium backdrop-blur-xl",
    glass: "rounded-4xl border border-white/60 bg-white/65 shadow-glow backdrop-blur-2xl",
    dark: "rounded-4xl border border-white/10 bg-luxury-ink text-white shadow-premium",
    muted: "rounded-3xl border border-slate-200 bg-luxury-mist shadow-soft"
  };

  return <div className={cn(variants[variant], className)} {...props} />;
}

export function CardHeader({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6 pb-3", className)} {...props} />;
}

export function CardTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn("font-heading text-xl font-semibold tracking-tight", className)}
      {...props}
    />
  );
}

export function CardDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("mt-2 text-sm leading-6 text-slate-600", className)} {...props} />;
}

export function CardContent({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6 pt-3", className)} {...props} />;
}

export function CardFooter({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex items-center p-6 pt-3", className)} {...props} />;
}
