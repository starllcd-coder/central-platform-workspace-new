"use client";

import { ErrorState } from "@/components/feedback/error-state";

export default function Error({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  console.error(error);

  return (
    <div>
      <ErrorState
        title="This page could not be loaded."
        description="Something went wrong while opening this Nexivo page. Please try again."
      />

      <div className="fixed bottom-6 left-1/2 z-[200] -translate-x-1/2">
        <button
          type="button"
          onClick={reset}
          className="rounded-full bg-luxury-ink px-6 py-3 text-sm font-semibold text-white shadow-premium"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
