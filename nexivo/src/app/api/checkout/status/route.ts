import { NextResponse } from "next/server";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import { CentralPlatformRequestError, centralPlatformRequest } from "@/lib/integrations/central-platform-api";
export async function POST(request: Request) {
  try {
    const body: unknown = await request.json();
    const result = await centralPlatformRequest("/checkout/status/", { method: "POST", body, timeoutMs: 20000 });
    return NextResponse.json(createApiSuccess(result,"central-platform"));
  } catch (error) {
    return NextResponse.json(createApiError("CHECKOUT_UNAVAILABLE", error instanceof CentralPlatformRequestError ? error.message : "Checkout is unavailable."), { status: error instanceof CentralPlatformRequestError ? error.status : 502 });
  }
}
