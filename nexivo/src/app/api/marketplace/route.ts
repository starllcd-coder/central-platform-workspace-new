import { NextResponse } from "next/server";
import { createApiSuccess } from "@/lib/api/api-response";
import { stayProperties } from "@/features/stays/data/stay-properties";
import { rentalVehicles } from "@/features/cars/data/rental-vehicles";
import { laundryProviders } from "@/features/laundry/data/laundry-providers";
import { destinations } from "@/features/geo/data/destinations";
import {
  centralPlatformFallbackEnabled,
  centralPlatformRequest,
  type CentralListResponse
} from "@/lib/integrations/central-platform-api";

type CentralListing = {
  module_code?: string;
  moduleCode?: string;
};

export async function GET() {
  try {
    const [listings, tenants] = await Promise.all([
      centralPlatformRequest<CentralListResponse<CentralListing>>("/listings/"),
      centralPlatformRequest<CentralListResponse<unknown>>("/tenants/")
    ]);
    const byModule = (moduleCode: string) =>
      listings.results.filter((listing) => (listing.module_code ?? listing.moduleCode) === moduleCode);

    return NextResponse.json(
      createApiSuccess(
        {
          stays: byModule("staylux"),
          cars: byModule("drivesphere"),
          laundry: byModule("laundrex"),
          destinations,
          tenants: tenants.results
        },
        "central-platform"
      )
    );
  } catch {
    if (!centralPlatformFallbackEnabled()) {
      return NextResponse.json({ success: false, error: { code: "CENTRAL_PLATFORM_UNAVAILABLE" } }, { status: 502 });
    }
    // Keep Nexivo usable during local development when Central Platform is not running.
  }

  return NextResponse.json(
    createApiSuccess({
      stays: stayProperties,
      cars: rentalVehicles,
      laundry: laundryProviders,
      destinations
    })
  );
}
