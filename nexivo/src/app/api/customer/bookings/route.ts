import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { NEXIVO_SESSION_COOKIE, verifySessionToken } from "@/lib/auth/session";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import { centralPlatformRequest } from "@/lib/integrations/central-platform-api";

export async function GET(request: Request) {
  try {
    const session = await verifySessionToken((await cookies()).get(NEXIVO_SESSION_COOKIE)?.value);
    const authHeader = request.headers.get("authorization") || (session ? `Bearer ${session.accessToken}` : "");
    const bookings = await centralPlatformRequest<unknown>("/customer/bookings/", {
      headers: authHeader ? { Authorization: authHeader } : {}
    });

    return NextResponse.json(createApiSuccess(bookings, "central-platform"));
  } catch {
    return NextResponse.json(createApiError("UNAUTHORIZED", "Customer bookings are unavailable."), {
      status: 401
    });
  }
}
