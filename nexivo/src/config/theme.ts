export const themeConfig = {
  defaultTheme: "light",
  availableThemes: ["light", "dark"] as const,
  brandMode: "premium-travel-saas",
  visualDirection: {
    style: "modern, elegant, unique, premium marketplace",
    layout: "mobile-first responsive grid",
    motion: "soft micro-interactions",
    cards: "large radius, subtle glass, premium shadows",
    imagery: "GCC travel, hospitality, mobility, laundry services"
  }
} as const;

export type ThemeName = (typeof themeConfig.availableThemes)[number];
