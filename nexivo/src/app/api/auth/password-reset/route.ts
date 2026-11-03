import { NextResponse } from "next/server";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import { CentralPlatformRequestError, centralPlatformRequest } from "@/lib/integrations/central-platform-api";

export async function POST(request: Request) {
  let body: unknown;
  try { body = await request.json(); }
  catch { return NextResponse.json(createApiError("INVALID_REQUEST", "A valid request is required."), { status: 400 }); }
  try {
    const result = await centralPlatformRequest<{ detail: string }>("/auth/password-reset/", { method: "POST", body, timeoutMs: 12000 });
    return NextResponse.json(createApiSuccess(result, "central-platform"));
  } catch (error) {
    return NextResponse.json(createApiError("PASSWORD_RESET_FAILED", error instanceof CentralPlatformRequestError ? error.message : "Password recovery is unavailable."), {
      status: error instanceof CentralPlatformRequestError ? error.status : 502
    });
  }
}
