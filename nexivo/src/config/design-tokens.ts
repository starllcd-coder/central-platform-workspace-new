export const designTokens = {
  radius: {
    xs: "0.375rem",
    sm: "0.5rem",
    md: "0.75rem",
    lg: "1rem",
    xl: "1.25rem",
    "2xl": "1.5rem",
    "3xl": "2rem",
    "4xl": "2.5rem"
  },
  shadow: {
    soft: "0 20px 60px rgba(15, 23, 42, 0.08)",
    premium: "0 30px 90px rgba(15, 23, 42, 0.14)",
    glow: "0 0 0 1px rgba(255,255,255,0.45), 0 30px 80px rgba(21,112,239,0.18)"
  },
  motion: {
    fast: 0.18,
    normal: 0.28,
    slow: 0.55
  }
} as const;

export const brandColors = {
  primary: "#1570ef",
  ink: "#101828",
  navy: "#071a3d",
  gold: "#c8a45d",
  sand: "#f6efe5",
  pearl: "#fbfaf7"
} as const;
