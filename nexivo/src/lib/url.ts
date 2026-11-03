export function absoluteUrl(path = "/") {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://nexivo.com";

  if (path.startsWith("http")) {
    return path;
  }

  return `${baseUrl}${path.startsWith("/") ? path : `/${path}`}`;
}

export function createCanonicalPath(path: string) {
  if (!path || path === "/") {
    return "/";
  }

  return path.startsWith("/") ? path : `/${path}`;
}
