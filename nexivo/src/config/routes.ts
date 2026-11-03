export const publicRoutes = [
  {
    path: "/",
    priority: 1.0,
    changeFrequency: "daily"
  },
  {
    path: "/stays",
    priority: 0.95,
    changeFrequency: "daily"
  },
  {
    path: "/cars",
    priority: 0.9,
    changeFrequency: "daily"
  },
  {
    path: "/laundry",
    priority: 0.85,
    changeFrequency: "daily"
  },
  {
    path: "/destinations",
    priority: 0.9,
    changeFrequency: "daily"
  },
  {
    path: "/business",
    priority: 0.85,
    changeFrequency: "weekly"
  },
  {
    path: "/business/solutions",
    priority: 0.8,
    changeFrequency: "weekly"
  },
  {
    path: "/business/staylux",
    priority: 0.8,
    changeFrequency: "weekly"
  },
  {
    path: "/business/drivesphere",
    priority: 0.8,
    changeFrequency: "weekly"
  },
  {
    path: "/business/laundrex",
    priority: 0.8,
    changeFrequency: "weekly"
  },
  {
    path: "/business/request-demo",
    priority: 0.75,
    changeFrequency: "weekly"
  },
  {
    path: "/pricing",
    priority: 0.75,
    changeFrequency: "weekly"
  },
  {
    path: "/about",
    priority: 0.65,
    changeFrequency: "monthly"
  },
  {
    path: "/contact",
    priority: 0.7,
    changeFrequency: "monthly"
  },
  {
    path: "/support",
    priority: 0.6,
    changeFrequency: "monthly"
  },
  {
    path: "/privacy",
    priority: 0.35,
    changeFrequency: "yearly"
  },
  {
    path: "/privacy/gdpr",
    priority: 0.35,
    changeFrequency: "yearly"
  },
  {
    path: "/terms",
    priority: 0.35,
    changeFrequency: "yearly"
  },
  {
    path: "/cookies",
    priority: 0.35,
    changeFrequency: "yearly"
  }
] as const;
