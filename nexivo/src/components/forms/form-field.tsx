import { cn } from "@/lib/utils";

type FormFieldProps = {
  label?: string;
  description?: string;
  error?: string;
  children: React.ReactNode;
  className?: string;
};

export function FormField({
  label,
  description,
  error,
  children,
  className
}: FormFieldProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {label ? <label className="text-sm font-semibold text-slate-800">{label}</label> : null}

      {children}

      {description && !error ? (
        <p className="text-xs leading-5 text-slate-500">{description}</p>
      ) : null}

      {error ? <p className="text-xs font-medium text-red-600">{error}</p> : null}
    </div>
  );
}
