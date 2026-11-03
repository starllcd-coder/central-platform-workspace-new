export function createRequestId(prefix = "req") {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

export function createApiSuccess<T>(
  data: T,
  source: "mock" | "central-platform" | "external" = "mock"
) {
  return {
    success: true,
    data,
    meta: {
      requestId: createRequestId(),
      timestamp: new Date().toISOString(),
      source
    }
  };
}

export function createApiError(code: string, message: string) {
  return {
    success: false,
    error: {
      code,
      message
    },
    meta: {
      requestId: createRequestId("err"),
      timestamp: new Date().toISOString(),
      source: "mock" as const
    }
  };
}
