import { NextResponse } from "next/server";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import {
  createSessionToken,
  NEXIVO_SESSION_COOKIE,
  NEXIVO_SESSION_MAX_AGE
} from "@/lib/auth/session";
import { centralPlatformRequest } from "@/lib/integrations/central-platform-api";
import type { AuthRole, AuthUser } from "@/features/auth/types/auth.types";

type CentralProviderAuthResponse = {
  accessToken: string;
  user: { id: string; name?: string; email: string; role?: string };
};

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const session = await centralPlatformRequest<CentralProviderAuthResponse, unknown>("/provider/login/", {
      method: "POST",
      body
    });
    const role: AuthRole = session.user.role === "admin" ? "admin" : "partner";
    const user: AuthUser = {
      id: session.user.id,
      fullName: session.user.name ?? session.user.email,
      email: session.user.email,
      role,
      preferredLanguage: "en",
      preferredCurrency: "OMR"
    };
    const expiresAt = Date.now() + NEXIVO_SESSION_MAX_AGE * 1000;
    const token = await createSessionToken({ accessToken: session.accessToken, user, role, expiresAt });
    const response = NextResponse.json(createApiSuccess({ user }, "central-platform"));
    response.cookies.set(NEXIVO_SESSION_COOKIE, token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: NEXIVO_SESSION_MAX_AGE
    });
    return response;
  } catch {
    return NextResponse.json(createApiError("PROVIDER_AUTH_FAILED", "Central Platform provider login failed."), {
      status: 401
    });
  }
}
