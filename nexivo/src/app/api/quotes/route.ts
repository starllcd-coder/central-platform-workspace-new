import { NextResponse } from "next/server";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import { CentralPlatformRequestError, centralPlatformRequest } from "@/lib/integrations/central-platform-api";
export async function POST(request: Request) {
  try {
    const body: unknown = await request.json();
    const quote = await centralPlatformRequest("/quotes/", { method: "POST", body, timeoutMs: 12000 });
    return NextResponse.json(createApiSuccess(quote, "central-platform"));
  } catch (error) {
    return NextResponse.json(createApiError("QUOTE_UNAVAILABLE", error instanceof CentralPlatformRequestError ? error.message : "Quote service is unavailable."), { status: error instanceof CentralPlatformRequestError ? error.status : 502 });
  }
}
