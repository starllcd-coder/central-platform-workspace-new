import { NextResponse } from "next/server";
import { createApiSuccess } from "@/lib/api/api-response";
import { mockCentralPlatformSnapshot } from "@/lib/mocks/central-platform-snapshot";
import { getLiveConnectors } from "@/lib/integrations/live-connectors";
import { integrationConnectors } from "@/features/integrations/data/integration-connectors";
import {
  centralPlatformFallbackEnabled,
  centralPlatformHealth,
  centralPlatformRequest,
  type CentralListResponse
} from "@/lib/integrations/central-platform-api";

export async function GET() {
  try {
    const [health, tenants, listings, connectors] = await Promise.all([
      centralPlatformHealth(),
      centralPlatformRequest<CentralListResponse<unknown>>("/tenants/"),
      centralPlatformRequest<CentralListResponse<unknown>>("/listings/"),
      getLiveConnectors()
    ]);

    return NextResponse.json(
      createApiSuccess(
        {
          health,
          snapshot: { generatedAt: new Date().toISOString(), tenants: tenants.results, listings: listings.results },
          connectors
        },
        "central-platform"
      )
    );
  } catch {
    if (!centralPlatformFallbackEnabled()) {
      return NextResponse.json(
        { success: false, error: { code: "CENTRAL_PLATFORM_UNAVAILABLE" } },
        { status: 502 }
      );
    }
  }

  return NextResponse.json(
    createApiSuccess({
      snapshot: mockCentralPlatformSnapshot,
      connectors: integrationConnectors
    })
  );
}
