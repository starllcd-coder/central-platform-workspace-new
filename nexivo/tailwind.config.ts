import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}"
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: "1.25rem",
        sm: "1.5rem",
        lg: "2rem",
        xl: "2.5rem",
        "2xl": "3rem"
      }
    },
    extend: {
      fontFamily: {
        heading: ["var(--font-heading)", "Manrope", "sans-serif"],
        body: ["var(--font-body)", "Inter", "sans-serif"],
        arabicHeading: ["var(--font-arabic-heading)", "IBM Plex Sans Arabic", "sans-serif"],
        arabicBody: ["var(--font-arabic-body)", "Tajawal", "sans-serif"]
      },
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        surface: "hsl(var(--surface))",
        surfaceMuted: "hsl(var(--surface-muted))",
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))"
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))"
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))"
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))"
        },
        success: {
          DEFAULT: "hsl(var(--success))",
          foreground: "hsl(var(--success-foreground))"
        },
        warning: {
          DEFAULT: "hsl(var(--warning))",
          foreground: "hsl(var(--warning-foreground))"
        },
        brand: {
          50: "#eef8ff",
          100: "#d9efff",
          200: "#b9e3ff",
          300: "#88d1ff",
          400: "#50b4ff",
          500: "#1570ef",
          600: "#0b5ed7",
          700: "#084db2",
          800: "#073f8d",
          900: "#062a61",
          950: "#041a3d"
        },
        luxury: {
          pearl: "#fbfaf7",
          mist: "#f8fafc",
          cloud: "#eef2f7",
          sand: "#f6efe5",
          dune: "#e8d8bd",
          gold: "#c8a45d",
          bronze: "#987542",
          ink: "#101828",
          navy: "#071a3d",
          charcoal: "#1f2937"
        },
        gcc: {
          oman: "#c43c2d",
          uae: "#00732f",
          saudi: "#006c35",
          qatar: "#8a1538",
          bahrain: "#ce1126",
          kuwait: "#007a3d"
        }
      },
      backgroundImage: {
        "nexivo-radial": "radial-gradient(circle at top left, rgba(21,112,239,0.16), transparent 35%), radial-gradient(circle at top right, rgba(200,164,93,0.18), transparent 35%)",
        "luxury-gradient": "linear-gradient(135deg, #fbfaf7 0%, #f8fafc 42%, #f6efe5 100%)",
        "midnight-gradient": "linear-gradient(135deg, #071a3d 0%, #101828 56%, #062a61 100%)",
        "gold-gradient": "linear-gradient(135deg, #c8a45d 0%, #e8d8bd 50%, #987542 100%)"
      },
      borderRadius: {
        xs: "0.375rem",
        sm: "0.5rem",
        md: "0.75rem",
        lg: "1rem",
        xl: "1.25rem",
        "2xl": "1.5rem",
        "3xl": "2rem",
        "4xl": "2.5rem",
        full: "9999px"
      },
      boxShadow: {
        soft: "0 20px 60px rgba(15, 23, 42, 0.08)",
        premium: "0 30px 90px rgba(15, 23, 42, 0.14)",
        glow: "0 0 0 1px rgba(255,255,255,0.45), 0 30px 80px rgba(21,112,239,0.18)",
        gold: "0 22px 60px rgba(200,164,93,0.28)"
      },
      animation: {
        "fade-up": "fadeUp 0.7s ease both",
        "scale-in": "scaleIn 0.45s ease both",
        "float-slow": "floatSlow 6s ease-in-out infinite",
        "pulse-soft": "pulseSoft 3s ease-in-out infinite"
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(18px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.96)" },
          "100%": { opacity: "1", transform: "scale(1)" }
        },
        floatSlow: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-12px)" }
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.72" }
        }
      }
    }
  },
  plugins: []
};

export default config;
