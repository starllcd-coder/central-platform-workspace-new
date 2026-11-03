"use client";

import * as React from "react";
import { CheckCircle2, Info, TriangleAlert, X, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export type ToastType = "success" | "error" | "warning" | "info";

export type ToastMessage = {
  id: string;
  title: string;
  description?: string;
  type?: ToastType;
};

type ToastContextValue = {
  toasts: ToastMessage[];
  showToast: (toast: Omit<ToastMessage, "id">) => void;
  dismissToast: (id: string) => void;
};

const ToastContext = React.createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastMessage[]>([]);

  const dismissToast = React.useCallback((id: string) => {
    setToasts((items) => items.filter((item) => item.id !== id));
  }, []);

  const showToast = React.useCallback(
    (toast: Omit<ToastMessage, "id">) => {
      const id = crypto.randomUUID();

      setToasts((items) => [
        ...items,
        {
          id,
          type: "info",
          ...toast
        }
      ]);

      window.setTimeout(() => dismissToast(id), 4500);
    },
    [dismissToast]
  );

  return (
    <ToastContext.Provider value={{ toasts, showToast, dismissToast }}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismissToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = React.useContext(ToastContext);

  if (!context) {
    throw new Error("useToast must be used inside ToastProvider.");
  }

  return context;
}

function ToastViewport({
  toasts,
  onDismiss
}: {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}) {
  return (
    <div className="fixed right-5 top-24 z-[120] grid w-[calc(100%-2.5rem)] max-w-sm gap-3">
      {toasts.map((toast) => (
        <ToastCard key={toast.id} toast={toast} onDismiss={() => onDismiss(toast.id)} />
      ))}
    </div>
  );
}

function ToastCard({
  toast,
  onDismiss
}: {
  toast: ToastMessage;
  onDismiss: () => void;
}) {
  const Icon = {
    success: CheckCircle2,
    error: XCircle,
    warning: TriangleAlert,
    info: Info
  }[toast.type ?? "info"];

  const colorClass = {
    success: "text-emerald-600 bg-emerald-50",
    error: "text-red-600 bg-red-50",
    warning: "text-amber-600 bg-amber-50",
    info: "text-brand-700 bg-brand-50"
  }[toast.type ?? "info"];

  return (
    <div className="flex gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-premium">
      <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl", colorClass)}>
        <Icon size={20} />
      </div>

      <div className="min-w-0 flex-1">
        <h3 className="text-sm font-semibold text-luxury-ink">{toast.title}</h3>
        {toast.description ? (
          <p className="mt-1 text-sm leading-5 text-slate-600">{toast.description}</p>
        ) : null}
      </div>

      <button
        type="button"
        onClick={onDismiss}
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-700"
        aria-label="Dismiss toast"
      >
        <X size={16} />
      </button>
    </div>
  );
}
