"use client";

import { ErrorState } from "@/components/feedback/error-state";

export default function GlobalError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  console.error(error);

  return (
    <html lang="en">
      <body>
        <div>
          <ErrorState
            title="Nexivo encountered a problem."
            description="An unexpected error occurred while loading this experience. You can try again or return to the homepage."
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
      </body>
    </html>
  );
}
