import { CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

type ChecklistProps = {
  items: string[];
  columns?: 1 | 2 | 3;
  className?: string;
};

export function Checklist({ items, columns = 2, className }: ChecklistProps) {
  const columnClass = {
    1: "grid-cols-1",
    2: "md:grid-cols-2",
    3: "md:grid-cols-2 lg:grid-cols-3"
  }[columns];

  return (
    <div className={cn("grid gap-3", columnClass, className)}>
      {items.map((item) => (
        <div
          key={item}
          className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-soft"
        >
          <CheckCircle2 size={18} className="shrink-0 text-emerald-600" />
          <span className="text-sm font-medium text-slate-700">{item}</span>
        </div>
      ))}
    </div>
  );
}
