export default function Loading() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-luxury-mist">
      <div className="rounded-4xl border border-slate-200 bg-white p-8 text-center shadow-premium">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-brand-600" />
        <p className="mt-5 font-heading text-xl font-semibold text-luxury-ink">
          Loading Nexivo...
        </p>
      </div>
    </main>
  );
}
