import { NextRequest, NextResponse } from "next/server";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import { NEXIVO_SESSION_COOKIE, verifySessionToken } from "@/lib/auth/session";

export async function GET(request: NextRequest) {
  const session = await verifySessionToken(request.cookies.get(NEXIVO_SESSION_COOKIE)?.value);
  if (!session) {
    return NextResponse.json(createApiError("UNAUTHENTICATED", "Authentication is required."), { status: 401 });
  }
  return NextResponse.json(createApiSuccess({ user: session.user }, "central-platform"));
}

export async function DELETE() {
  const response = NextResponse.json(createApiSuccess({ loggedOut: true }, "central-platform"));
  response.cookies.delete(NEXIVO_SESSION_COOKIE);
  return response;
}
