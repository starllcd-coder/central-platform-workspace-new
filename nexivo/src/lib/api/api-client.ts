type RequestMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

type RequestOptions<TBody = unknown> = {
  method?: RequestMethod;
  body?: TBody;
  headers?: Record<string, string>;
  cache?: RequestCache;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_SITE_URL ||
  "http://localhost:3000";

export async function apiRequest<TResponse, TBody = unknown>(
  path: string,
  options: RequestOptions<TBody> = {}
): Promise<TResponse> {
  const url = path.startsWith("http")
    ? path
    : `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;

  const response = await fetch(url, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: options.cache ?? "no-store"
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  return response.json() as Promise<TResponse>;
}

export const apiClient = {
  get: <TResponse>(path: string) =>
    apiRequest<TResponse>(path, { method: "GET" }),

  post: <TResponse, TBody = unknown>(path: string, body: TBody) =>
    apiRequest<TResponse, TBody>(path, { method: "POST", body }),

  put: <TResponse, TBody = unknown>(path: string, body: TBody) =>
    apiRequest<TResponse, TBody>(path, { method: "PUT", body }),

  patch: <TResponse, TBody = unknown>(path: string, body: TBody) =>
    apiRequest<TResponse, TBody>(path, { method: "PATCH", body }),

  delete: <TResponse>(path: string) =>
    apiRequest<TResponse>(path, { method: "DELETE" })
};
