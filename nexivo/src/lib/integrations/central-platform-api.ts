type CentralRequestOptions<TBody = unknown> = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: TBody;
  rawBody?: string;
  headers?: Record<string, string>;
  timeoutMs?: number;
};

export class CentralPlatformRequestError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "CentralPlatformRequestError";
    this.status = status;
  }
}

const CENTRAL_API_BASE_URL = (
  process.env.CENTRAL_PLATFORM_API_URL ||
  process.env.NEXT_PUBLIC_CENTRAL_PLATFORM_API ||
  "http://127.0.0.1:8000/api"
).replace(/\/$/, "");

function centralUrl(path: string) {
  return path.startsWith("http")
    ? path
    : `${CENTRAL_API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

export async function centralPlatformRequest<TResponse, TBody = unknown>(
  path: string,
  options: CentralRequestOptions<TBody> = {}
): Promise<TResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs ?? 2500);

  try {
    const response = await fetch(centralUrl(path), {
      method: options.method ?? "GET",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers ?? {})
      },
      body:
        options.rawBody ??
        (options.body === undefined ? undefined : JSON.stringify(options.body)),
      cache: "no-store",
      signal: controller.signal
    });

    const contentType = response.headers.get("content-type") ?? "";
    const payload = contentType.includes("application/json") ? await response.json() : await response.text();

    if (!response.ok) {
      const detail =
        typeof payload === "object" && payload && "detail" in payload
          ? String((payload as { detail?: unknown }).detail)
          : `Central Platform request failed with status ${response.status}`;
      throw new CentralPlatformRequestError(detail, response.status);
    }

    return payload as TResponse;
  } finally {
    clearTimeout(timeout);
  }
}

export type CentralListResponse<T> = {
  results: T[];
};

export async function centralPlatformHealth() {
  return centralPlatformRequest<{ status?: string; service?: string }>("/health/");
}

export function centralPlatformFallbackEnabled() {
  const configured = process.env.NEXIVO_ALLOW_MOCK_FALLBACK;
  if (configured !== undefined) return configured === "1";
  return process.env.NODE_ENV !== "production";
}
