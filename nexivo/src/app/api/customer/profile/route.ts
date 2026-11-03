import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { NEXIVO_SESSION_COOKIE, verifySessionToken } from "@/lib/auth/session";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import { centralPlatformRequest } from "@/lib/integrations/central-platform-api";

export async function GET(request: Request) {
  try {
    const session = await verifySessionToken((await cookies()).get(NEXIVO_SESSION_COOKIE)?.value);
    const authHeader = request.headers.get("authorization") || (session ? `Bearer ${session.accessToken}` : "");
    const profile = await centralPlatformRequest<unknown>("/customer/profile/", {
      headers: authHeader ? { Authorization: authHeader } : {}
    });

    return NextResponse.json(createApiSuccess(profile, "central-platform"));
  } catch {
    return NextResponse.json(createApiError("UNAUTHORIZED", "Customer profile is unavailable."), {
      status: 401
    });
  }
}
