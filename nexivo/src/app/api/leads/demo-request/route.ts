import { createHmac, randomUUID } from "node:crypto";
import { NextResponse } from "next/server";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import { centralPlatformFallbackEnabled, centralPlatformRequest } from "@/lib/integrations/central-platform-api";
import { demoRequestSchema } from "@/features/leads/schemas/demo-request.schema";

export async function POST(request: Request) {
  try {
    const parsed = demoRequestSchema.safeParse(await request.json());
    if (!parsed.success) {
      return NextResponse.json(createApiError("INVALID_REQUEST", parsed.error.issues[0]?.message ?? "Invalid demo request lead."), {
        status: 400
      });
    }
    const body = parsed.data;
    const leadReference = (request.headers.get("Idempotency-Key") || randomUUID()).slice(0, 120);
    const secret = process.env.NEXIVO_LEAD_SHARED_SECRET;
    if (!secret) {
      return NextResponse.json(createApiError("SERVER_MISCONFIGURED", "Demo request integration is not configured."), {
        status: 500
      });
    }
    const timestamp = Math.floor(Date.now() / 1000).toString();
    const rawBody = JSON.stringify(body);
    const signature = createHmac("sha256", secret)
      .update(`${timestamp}.${leadReference}.${rawBody}`)
      .digest("hex");

    try {
      const lead = await centralPlatformRequest<unknown, unknown>("/leads/", {
        method: "POST",
        body,
        rawBody,
        headers: {
          "X-Nexivo-Timestamp": timestamp,
          "X-Nexivo-Signature": signature,
          "X-Idempotency-Key": leadReference
        }
      });
      return NextResponse.json(createApiSuccess(lead, "central-platform"), { status: 201 });
    } catch {
      if (!centralPlatformFallbackEnabled()) {
        return NextResponse.json(createApiError("CENTRAL_PLATFORM_UNAVAILABLE", "Central Platform lead capture is unavailable."), {
          status: 502
        });
      }
      // Keep demo lead capture available when Central Platform is offline.
    }

    return NextResponse.json(
      createApiSuccess({
        leadReference,
        status: "new",
        assignedTo: "DSS Sales",
        nextStep: "Schedule demo and prepare custom proposal.",
        payload: body
      })
    );
  } catch {
    return NextResponse.json(createApiError("INVALID_REQUEST", "Invalid demo request lead."), {
      status: 400
    });
  }
}
