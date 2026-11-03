import { NextResponse } from "next/server";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import {
  createSessionToken,
  NEXIVO_SESSION_COOKIE,
  NEXIVO_SESSION_MAX_AGE
} from "@/lib/auth/session";
import { centralPlatformRequest } from "@/lib/integrations/central-platform-api";
import type { AuthUser } from "@/features/auth/types/auth.types";

type CentralRegistrationResponse = {
  accessToken: string;
  user: { id: string; name?: string; fullName?: string; email: string };
};

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const session = await centralPlatformRequest<CentralRegistrationResponse, unknown>("/auth/register/", {
      method: "POST",
      body
    });
    const user: AuthUser = {
      id: session.user.id,
      fullName: session.user.fullName ?? session.user.name ?? session.user.email,
      email: session.user.email,
      role: "customer",
      preferredLanguage: "en",
      preferredCurrency: "OMR"
    };
    const expiresAt = Date.now() + NEXIVO_SESSION_MAX_AGE * 1000;
    const token = await createSessionToken({ accessToken: session.accessToken, user, role: "customer", expiresAt });
    const response = NextResponse.json(createApiSuccess({ user }, "central-platform"), { status: 201 });
    response.cookies.set(NEXIVO_SESSION_COOKIE, token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: NEXIVO_SESSION_MAX_AGE
    });
    return response;
  } catch {
    return NextResponse.json(createApiError("REGISTRATION_FAILED", "Central Platform registration failed."), {
      status: 400
    });
  }
}
