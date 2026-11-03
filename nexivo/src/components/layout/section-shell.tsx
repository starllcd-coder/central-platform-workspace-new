import { cn } from "@/lib/utils";

type SectionShellProps = {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
  background?: "default" | "muted" | "dark" | "gradient";
};

export function SectionShell({
  children,
  className,
  containerClassName,
  background = "default"
}: SectionShellProps) {
  const backgroundClass = {
    default: "bg-background",
    muted: "bg-luxury-mist",
    dark: "bg-midnight-gradient text-white",
    gradient: "bg-nexivo-radial"
  }[background];

  return (
    <section className={cn("section-padding", backgroundClass, className)}>
      <div className={cn("nexivo-container", containerClassName)}>{children}</div>
    </section>
  );
}
