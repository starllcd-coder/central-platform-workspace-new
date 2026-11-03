import { Compass, Home, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PublicPageLayout } from "@/components/layout/public-page-layout";

export function NotFoundState() {
  return (
    <PublicPageLayout includeJsonLd={false}>
      <section className="bg-nexivo-radial">
        <div className="nexivo-container flex min-h-[68vh] items-center justify-center py-20">
          <div className="max-w-2xl text-center">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-4xl bg-brand-50 text-brand-700 shadow-soft">
              <Compass size={34} />
            </div>

            <p className="eyebrow mb-5">404</p>

            <h1 className="font-heading text-4xl font-semibold tracking-tight text-luxury-ink md:text-6xl">
              This Nexivo page was not found.
            </h1>

            <p className="mx-auto mt-5 max-w-xl text-base leading-8 text-slate-600">
              The page may have moved, the link may be incorrect, or this section may still be planned for a future Nexivo release.
            </p>

            <div className="mt-9 flex flex-wrap justify-center gap-3">
              <Button asChild variant="luxury" size="lg">
                <a href="/">
                  <Home className="mr-2" size={18} />
                  Go Home
                </a>
              </Button>

              <Button asChild variant="outline" size="lg">
                <a href="/destinations">
                  <Search className="mr-2" size={18} />
                  Explore Destinations
                </a>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </PublicPageLayout>
  );
}
