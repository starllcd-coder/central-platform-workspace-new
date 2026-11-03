import type { Metadata, Viewport } from "next";
import { Inter, Manrope, IBM_Plex_Sans_Arabic, Tajawal } from "next/font/google";
import { ToastProvider } from "@/components/feedback/toast";
import { CookieBanner } from "@/features/privacy/components/cookie-banner";
import { LocaleHtmlSync } from "@/features/localization/components/locale-html-sync";
import { SkipToContent } from "@/components/accessibility/skip-to-content";
import { BackToTopButton } from "@/components/accessibility/back-to-top-button";
import "@/styles/globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap"
});

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-heading",
  display: "swap"
});

const ibmArabic = IBM_Plex_Sans_Arabic({
  subsets: ["arabic"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-arabic-heading",
  display: "swap"
});

const tajawal = Tajawal({
  subsets: ["arabic"],
  weight: ["400", "500", "700"],
  variable: "--font-arabic-body",
  display: "swap"
});

export const metadata: Metadata = {
  title: {
    default: "Nexivo | Stays, Cars & Laundry in One Platform",
    template: "%s | Nexivo"
  },
  description:
    "Nexivo is a GCC-first, Europe-ready travel and services marketplace for stays, car rentals, and laundry services, powered by DSS.",
  applicationName: "Nexivo",
  authors: [{ name: "Deedarian Software Solutions" }],
  creator: "Deedarian Software Solutions",
  publisher: "Deedarian Software Solutions",
  metadataBase: new URL("https://nexivo.com"),
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    title: "Nexivo",
    statusBarStyle: "black-translucent"
  },
  openGraph: {
    title: "Nexivo",
    description: "Book stays, rent cars, and manage travel services in one seamless platform.",
    siteName: "Nexivo",
    type: "website"
  }
};

export const viewport: Viewport = {
  themeColor: "#0f172a"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <body
        suppressHydrationWarning
        className={`${inter.variable} ${manrope.variable} ${ibmArabic.variable} ${tajawal.variable} bg-background font-body text-foreground antialiased`}
      >
        <ToastProvider>
          <LocaleHtmlSync />
          <SkipToContent />
          <div id="main-content">{children}</div>
          <BackToTopButton />
          <CookieBanner />
        </ToastProvider>
      </body>
    </html>
  );
}
