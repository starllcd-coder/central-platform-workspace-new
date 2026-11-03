import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { SectionHeading } from "@/components/layout/section-heading";
import { SectionShell } from "@/components/layout/section-shell";
import { PremiumFeatureCard } from "@/components/blocks/premium-feature-card";
import { MetricCard } from "@/components/stats/metric-card";
import { CtaBand } from "@/components/marketing/cta-band";
import { GradientPanel } from "@/components/blocks/gradient-panel";
import { Checklist } from "@/components/blocks/checklist";
import { Badge, Button, Card, CardContent, CardHeader, CardTitle, Input, Tabs } from "@/components/ui";
import { designPrinciples, platformHighlights } from "@/data/design-system-data";
import { Car, Hotel, Search, Shirt } from "lucide-react";

export default function DesignSystemPage() {
  return (
    <main className="min-h-screen bg-luxury-mist">
      <SiteHeader />

      <SectionShell background="gradient" className="pt-20">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <p className="eyebrow mb-5">Design System</p>

            <h1 className="font-heading text-5xl font-semibold tracking-tight text-luxury-ink md:text-7xl">
              Nexivo premium interface foundation.
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              Modern, elegant, GCC-first, Europe-ready design blocks for the Nexivo marketplace,
              DSS business website, partner portal, and future global expansion.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Button variant="luxury" size="lg">Primary Action</Button>
              <Button variant="outline" size="lg">Secondary Action</Button>
              <Button variant="gold" size="lg">Premium CTA</Button>
            </div>
          </div>

          <GradientPanel>
            <div className="grid gap-4">
              <div className="grid grid-cols-3 gap-3">
                <button className="rounded-3xl bg-luxury-ink p-4 text-left text-white">
                  <Hotel size={24} />
                  <span className="mt-4 block font-semibold">Stays</span>
                </button>
                <button className="rounded-3xl bg-white p-4 text-left shadow-soft">
                  <Car size={24} />
                  <span className="mt-4 block font-semibold">Cars</span>
                </button>
                <button className="rounded-3xl bg-white p-4 text-left shadow-soft">
                  <Shirt size={24} />
                  <span className="mt-4 block font-semibold">Laundry</span>
                </button>
              </div>

              <div className="rounded-4xl bg-white p-4 shadow-premium">
                <div className="grid gap-3 md:grid-cols-[1fr_auto]">
                  <Input leftIcon={<Search size={17} />} placeholder="Search Salalah, Dubai, Doha..." />
                  <Button variant="default">Search</Button>
                </div>
              </div>
            </div>
          </GradientPanel>
        </div>
      </SectionShell>

      <SectionShell background="default">
        <SectionHeading
          eyebrow="Platform Ecosystem"
          title="One visual system for all Nexivo products."
          description="Reusable cards, layouts, metrics, and action blocks support the marketplace, DSS marketing pages, customer portal, and partner portal."
        />

        <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {platformHighlights.map((item) => (
            <PremiumFeatureCard
              key={item.title}
              title={item.title}
              description={item.description}
              icon={item.icon}
              tone={item.tone}
            />
          ))}
        </div>
      </SectionShell>

      <SectionShell background="muted">
        <SectionHeading
          eyebrow="Design Principles"
          title="Built to feel premium, trustworthy, and unique."
          align="center"
        />

        <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {designPrinciples.map((item) => (
            <PremiumFeatureCard
              key={item.title}
              title={item.title}
              description={item.description}
              icon={item.icon}
              tone="neutral"
            />
          ))}
        </div>
      </SectionShell>

      <SectionShell background="default">
        <div className="grid gap-5 md:grid-cols-3">
          <MetricCard label="Launch Region" value="GCC" description="Oman, UAE, Saudi Arabia, Qatar, Bahrain, Kuwait." />
          <MetricCard label="Languages" value="10+" description="English, Arabic, and key European languages." />
          <MetricCard label="Currencies" value="11+" description="GCC currencies plus EUR, GBP, USD, CHF, and TRY." />
        </div>
      </SectionShell>

      <SectionShell background="default">
        <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
          <Card variant="premium">
            <CardHeader>
              <CardTitle>Component Samples</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="flex flex-wrap gap-2">
                <Badge>Default</Badge>
                <Badge variant="luxury">Luxury</Badge>
                <Badge variant="gold">Premium</Badge>
                <Badge variant="success">Verified</Badge>
                <Badge variant="warning">Featured</Badge>
              </div>

              <Tabs
                variant="premium"
                items={[
                  { value: "stays", label: "Stays" },
                  { value: "cars", label: "Cars" },
                  { value: "laundry", label: "Laundry" }
                ]}
                defaultValue="stays"
              />

              <Input placeholder="Premium input field" />

              <div className="flex flex-wrap gap-3">
                <Button variant="default">Default</Button>
                <Button variant="luxury">Luxury</Button>
                <Button variant="gold">Gold</Button>
                <Button variant="outline">Outline</Button>
              </div>
            </CardContent>
          </Card>

          <Card variant="premium">
            <CardHeader>
              <CardTitle>Nexivo Launch Design Requirements</CardTitle>
            </CardHeader>
            <CardContent>
              <Checklist
                columns={2}
                items={[
                  "Modern and elegant visual identity",
                  "Unique premium marketplace layout",
                  "Mobile-first responsive design",
                  "English and Arabic RTL support",
                  "European language readiness",
                  "Multi-currency selector",
                  "Partner/business section",
                  "Customer booking-first homepage",
                  "DSS Central Platform integration",
                  "Future GDPR readiness"
                ]}
              />
            </CardContent>
          </Card>
        </div>
      </SectionShell>

      <SectionShell background="default">
        <CtaBand
          title="Nexivo is designed as a premium marketplace, not a generic booking website."
          description="The interface must make customers feel they are booking trusted travel services while businesses see DSS as a serious SaaS technology partner."
          primaryLabel="View Marketplace"
          primaryHref="/"
          secondaryLabel="For Business"
          secondaryHref="/business"
        />
      </SectionShell>

      <SiteFooter />
    </main>
  );
}
