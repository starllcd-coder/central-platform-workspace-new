import { NextResponse } from "next/server";
import { createApiSuccess } from "@/lib/api/api-response";
import { rentalVehicles } from "@/features/cars/data/rental-vehicles";
import {
  centralPlatformFallbackEnabled,
  centralPlatformRequest,
  type CentralListResponse
} from "@/lib/integrations/central-platform-api";

export async function GET() {
  try {
    const listings = await centralPlatformRequest<CentralListResponse<unknown>>("/listings/?module=drivesphere");
    return NextResponse.json(createApiSuccess(listings.results, "central-platform"));
  } catch {
    if (!centralPlatformFallbackEnabled()) {
      return NextResponse.json({ success: false, error: { code: "CENTRAL_PLATFORM_UNAVAILABLE" } }, { status: 502 });
    }
    // Keep static marketplace content available when Central Platform is offline.
  }

  return NextResponse.json(createApiSuccess(rentalVehicles));
}
