export function PwaInstallHint() {
  return (
    <div className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft">
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-brand-700">
        PWA Ready
      </p>
      <h3 className="mt-2 font-heading text-xl font-semibold text-luxury-ink">
        Nexivo can be installed like an app.
      </h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        The website includes manifest readiness for future installable customer and business
        experiences.
      </p>
    </div>
  );
}
