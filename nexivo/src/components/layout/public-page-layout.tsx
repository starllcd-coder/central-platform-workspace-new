import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";

type PublicPageLayoutProps = {
  children: React.ReactNode;
  includeJsonLd?: boolean;
};

export function PublicPageLayout({
  children,
  includeJsonLd = true
}: PublicPageLayoutProps) {
  return (
    <main className="min-h-screen bg-background" data-json-ld={includeJsonLd ? "true" : "false"}>
      <SiteHeader />
      {children}
      <SiteFooter />
    </main>
  );
}
