export const launchChecklist = [
  {
    title: "Customer marketplace",
    status: "ready",
    items: [
      "StayLux search and booking start flow",
      "DriveSphere search and rental start flow",
      "Laundrex provider search and order start flow",
      "Destination pages and cross-sell journey",
      "Customer account dashboard"
    ]
  },
  {
    title: "Business marketing",
    status: "ready",
    items: [
      "DSS business landing page",
      "StayLux product page",
      "DriveSphere product page",
      "Laundrex product page",
      "Central Platform page",
      "Pricing and demo request pages"
    ]
  },
  {
    title: "Commercial model",
    status: "ready",
    items: [
      "200 OMR starting setup fee displayed",
      "Exact commission percentages hidden publicly",
      "StayLux and DriveSphere commission model prepared",
      "Laundrex subscription model prepared",
      "Pricing remains adjustable in Central Platform"
    ]
  },
  {
    title: "Regional expansion",
    status: "ready",
    items: [
      "GCC countries and cities prepared",
      "Currency and timezone settings prepared",
      "English and Arabic RTL ready",
      "European languages prepared as fallback",
      "GDPR and consent pages prepared"
    ]
  },
  {
    title: "Technical readiness",
    status: "mock-ready",
    items: [
      "Mock API endpoints prepared",
      "Central Platform connectors prepared",
      "Admin monitoring prepared",
      "Audit logs prepared",
      "PWA manifest prepared"
    ]
  },
  {
    title: "Pending real integrations",
    status: "pending",
    items: [
      "Real database connection",
      "Payment gateway integration",
      "SMS / WhatsApp / email providers",
      "Map provider",
      "Video hosting for demos",
      "Production authentication"
    ]
  }
] as const;

export const qaChecklist = [
  "Run npm install",
  "Run npm run lint",
  "Run npm run build",
  "Check all public routes",
  "Check mobile navigation",
  "Check Arabic RTL display",
  "Check currency/language selectors",
  "Check booking flows for stays, cars, and laundry",
  "Check partner portal pages",
  "Check admin console pages",
  "Replace mock images if needed",
  "Connect real DSS Central Platform APIs",
  "Connect payment gateway before accepting real cards"
] as const;
