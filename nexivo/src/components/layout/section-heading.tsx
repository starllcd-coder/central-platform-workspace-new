import { cn } from "@/lib/utils";

type SectionHeadingProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "left" | "center";
  className?: string;
};

export function SectionHeading({
  eyebrow,
  title,
  description,
  align = "left",
  className
}: SectionHeadingProps) {
  return (
    <div
      className={cn(
        "max-w-3xl",
        align === "center" && "mx-auto text-center",
        className
      )}
    >
      {eyebrow ? <p className="eyebrow mb-5">{eyebrow}</p> : null}

      <h2 className="text-3xl font-semibold tracking-tight text-luxury-ink md:text-5xl dark:text-white">
        {title}
      </h2>

      {description ? (
        <p className="mt-5 text-base leading-8 text-slate-600 md:text-lg dark:text-slate-300">
          {description}
        </p>
      ) : null}
    </div>
  );
}
