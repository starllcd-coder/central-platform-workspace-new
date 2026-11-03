import { NextResponse } from "next/server";
import { createApiSuccess } from "@/lib/api/api-response";
import { centralPlatformHealth } from "@/lib/integrations/central-platform-api";

export async function GET() {
  let centralPlatform: { connected: boolean; status?: string; service?: string } = { connected: false };

  try {
    const health = await centralPlatformHealth();
    centralPlatform = {
      connected: true,
      status: health.status,
      service: health.service
    };
  } catch {
    centralPlatform = { connected: false };
  }

  return NextResponse.json(
    createApiSuccess({
      app: "Nexivo",
      status: "ok",
      environment: process.env.NODE_ENV ?? "development",
      centralPlatform,
      timestamp: new Date().toISOString()
    }, centralPlatform.connected ? "central-platform" : "mock")
  );
}
