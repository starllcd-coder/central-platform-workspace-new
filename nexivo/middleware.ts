import { NextRequest, NextResponse } from "next/server";
import { NEXIVO_SESSION_COOKIE, verifySessionToken } from "./src/lib/auth/session";

export async function middleware(request: NextRequest) {
  const session = await verifySessionToken(request.cookies.get(NEXIVO_SESSION_COOKIE)?.value);
  const path = request.nextUrl.pathname;
  const loginPath = path.startsWith("/partner") || path.startsWith("/admin") ? "/partner-login" : "/login";

  if (!session) {
    return NextResponse.redirect(new URL(loginPath, request.url));
  }

  const allowed = path.startsWith("/customer")
    ? session.role === "customer"
    : path.startsWith("/admin")
      ? session.role === "admin"
      : session.role === "partner" || session.role === "admin";

  if (!allowed) {
    const destination = session.role === "customer" ? "/customer" : session.role === "admin" ? "/admin" : "/partner";
    return NextResponse.redirect(new URL(destination, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/customer/:path*", "/partner/:path*", "/admin/:path*"]
};
