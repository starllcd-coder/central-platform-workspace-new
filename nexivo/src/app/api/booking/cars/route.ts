import { NextResponse } from "next/server";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import { CentralPlatformRequestError, centralPlatformRequest } from "@/lib/integrations/central-platform-api";

export async function POST(request: Request) {
  let body: Record<string, unknown>;
  try {
    const parsed: unknown = await request.json();
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("Invalid body");
    body = parsed as Record<string, unknown>;
  } catch {
    return NextResponse.json(createApiError("INVALID_REQUEST", "A booking request is required."), { status: 400 });
  }
  try {
    const booking = await centralPlatformRequest<unknown, unknown>("/bookings/", {
      method: "POST",
      body: { ...body, product: "drivesphere", moduleCode: "drivesphere" }
    });
    return NextResponse.json(createApiSuccess(booking, "central-platform"), { status: 201 });
  } catch (error) {
    if (error instanceof CentralPlatformRequestError) {
      return NextResponse.json(createApiError("BOOKING_REJECTED", error.message), { status: error.status });
    }
    return NextResponse.json(createApiError("CENTRAL_PLATFORM_UNAVAILABLE", "Booking could not be confirmed. Please try again."), { status: 502 });
  }
}
