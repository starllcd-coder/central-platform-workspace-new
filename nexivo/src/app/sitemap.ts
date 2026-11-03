import { MetadataRoute } from "next";

const baseUrl = "https://nexivo.com";

const routes = [
  "",
  "/stays",
  "/cars",
  "/laundry",
  "/destinations",
  "/business",
  "/business/staylux",
  "/business/drivesphere",
  "/business/laundrex",
  "/business/central-platform",
  "/pricing",
  "/business/request-demo",
  "/about",
  "/contact",
  "/support",
  "/faq",
  "/privacy",
  "/cookie-center",
  "/security",
  "/integrations",
  "/launch-readiness"
];

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: route === "" ? "daily" : "weekly",
    priority: route === "" ? 1 : 0.8
  }));
}
