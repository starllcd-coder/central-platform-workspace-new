import { AlertTriangle, ArrowLeft, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PublicPageLayout } from "@/components/layout/public-page-layout";

type ErrorStateProps = {
  title?: string;
  description?: string;
  showHome?: boolean;
  showBack?: boolean;
};

export function ErrorState({
  title = "Something went wrong",
  description = "We could not complete this request. Please try again or return to the homepage.",
  showHome = true,
  showBack = true
}: ErrorStateProps) {
  return (
    <PublicPageLayout includeJsonLd={false}>
      <section className="bg-nexivo-radial">
        <div className="nexivo-container flex min-h-[68vh] items-center justify-center py-20">
          <div className="max-w-2xl text-center">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-4xl bg-amber-50 text-amber-600 shadow-soft">
              <AlertTriangle size={34} />
            </div>

            <h1 className="font-heading text-4xl font-semibold tracking-tight text-luxury-ink md:text-6xl">
              {title}
            </h1>

            <p className="mx-auto mt-5 max-w-xl text-base leading-8 text-slate-600">
              {description}
            </p>

            <div className="mt-9 flex flex-wrap justify-center gap-3">
              {showHome ? (
                <Button asChild variant="luxury" size="lg">
                  <a href="/">
                    <Home className="mr-2" size={18} />
                    Go Home
                  </a>
                </Button>
              ) : null}

              {showBack ? (
                <Button asChild variant="outline" size="lg">
                  <a href="javascript:history.back()">
                    <ArrowLeft className="mr-2" size={18} />
                    Go Back
                  </a>
                </Button>
              ) : null}
            </div>
          </div>
        </div>
      </section>
    </PublicPageLayout>
  );
}
