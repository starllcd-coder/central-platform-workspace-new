import { LoadingSpinner } from "@/components/feedback/loading-spinner";

export function PageLoadingState() {
  return (
    <main className="min-h-screen bg-luxury-gradient">
      <div className="nexivo-container flex min-h-screen items-center justify-center">
        <div className="rounded-4xl border border-white/70 bg-white/85 p-10 text-center shadow-premium backdrop-blur-xl">
          <div className="mx-auto mb-6 h-16 w-16 rounded-4xl bg-midnight-gradient shadow-soft" />
          <LoadingSpinner label="Loading Nexivo experience..." />
        </div>
      </div>
    </main>
  );
}
