import { BrandMark } from "@/components/brand/brand-mark";
import { footerNavigation } from "@/config/navigation";

const trustBadges = ["GCC-first", "Europe-ready", "GDPR-ready", "Secure booking-ready"];

export function SiteFooter() {
  return (
    <footer className="border-t border-luxury-dune/70 bg-[linear-gradient(180deg,#fffdf8_0%,#f8fafc_100%)]">
      <div className="nexivo-container py-12 md:py-16">
        <div className="grid gap-10 lg:grid-cols-[0.95fr_1.55fr] lg:gap-16">
          <div>
            <BrandMark />
            <p className="mt-5 max-w-md text-sm leading-7 text-slate-600">
              Nexivo is a GCC-first, Europe-ready marketplace for stays, car rentals, and laundry
              services, powered by Deedarian Software Solutions.
            </p>

            <div className="mt-6 flex max-w-md flex-wrap gap-2">
              {trustBadges.map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-luxury-dune/70 bg-white/85 px-4 py-2 text-xs font-bold uppercase tracking-[0.12em] text-luxury-ink shadow-soft"
                >
                  {item}
                </span>
              ))}
            </div>

            <div className="mt-6 grid max-w-md grid-cols-2 gap-3">
              {["StayLux", "DriveSphere", "Laundrex", "DSS Central"].map((item) => (
                <div
                  key={item}
                  className="rounded-2xl border border-luxury-dune/70 bg-white/80 px-4 py-3 text-sm font-semibold text-luxury-ink shadow-soft"
                >
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {footerNavigation.map((group) => (
              <nav key={group.title} aria-label={`${group.title} footer links`}>
                <h3 className="font-heading text-base font-semibold text-luxury-ink">
                  {group.title}
                </h3>

                <ul className="mt-4 space-y-2.5">
                  {group.links.map((link) => (
                    <li key={link.href}>
                      <a
                        href={link.href}
                        className="text-sm font-medium text-slate-600 transition-colors hover:text-luxury-bronze"
                      >
                        {link.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </nav>
            ))}
          </div>
        </div>

        <div className="mt-10 grid gap-5 border-t border-luxury-dune/70 pt-6 md:grid-cols-[1fr_auto] md:items-center">
          <p className="max-w-3xl text-sm leading-7 text-slate-600">
            Nexivo commercial terms, commissions, subscriptions, setup fees, sponsored placements,
            payment gateways, integrations, countries, languages, currencies, and compliance rules are
            designed to remain configurable from DSS Central Platform.
          </p>

          <p className="text-sm font-semibold text-slate-500">
            © {new Date().getFullYear()} Deedarian Software Solutions. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}