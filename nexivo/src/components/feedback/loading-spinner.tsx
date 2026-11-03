import { cn } from "@/lib/utils";

type LoadingSpinnerProps = {
  className?: string;
  label?: string;
};

export function LoadingSpinner({ className, label = "Loading" }: LoadingSpinnerProps) {
  return (
    <div className={cn("inline-flex items-center gap-3 text-sm text-slate-600", className)}>
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-primary" />
      <span>{label}</span>
    </div>
  );
}
