import { NextResponse } from "next/server";
import { createApiError } from "@/lib/api/api-response";

export async function POST() {
  return NextResponse.json(
    createApiError("SYNC_NOT_IMPLEMENTED", "Use the supported booking, listing, and demo request flows."),
    { status: 501 }
  );
}
