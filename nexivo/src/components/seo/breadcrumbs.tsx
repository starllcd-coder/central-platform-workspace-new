type BreadcrumbsProps = {
  items: {
    label: string;
    href: string;
  }[];
};

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  return (
    <nav aria-label="Breadcrumb" className="text-sm text-slate-500">
      <ol className="flex flex-wrap items-center gap-2">
        {items.map((item, index) => (
          <li key={item.href} className="flex items-center gap-2">
            {index > 0 ? <span className="text-slate-300">/</span> : null}
            <a href={item.href} className="font-medium hover:text-brand-700">
              {item.label}
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}
