import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { NEXIVO_SESSION_COOKIE, verifySessionToken } from "@/lib/auth/session";
import { createApiError, createApiSuccess } from "@/lib/api/api-response";
import { CentralPlatformRequestError, centralPlatformRequest } from "@/lib/integrations/central-platform-api";
export async function POST(request: Request) {
  const session=await verifySessionToken((await cookies()).get(NEXIVO_SESSION_COOKIE)?.value);
  if(!session || !["admin","partner"].includes(session.role))return NextResponse.json(createApiError("UNAUTHORIZED","Sign in to your business account."),{status:401});
  try{
    const body:unknown=await request.json();
    const result=await centralPlatformRequest("/provider/sso-ticket/",{method:"POST",body,headers:{Authorization:`Bearer ${session.accessToken}`}});
    return NextResponse.json(createApiSuccess(result,"central-platform"));
  }catch(error){return NextResponse.json(createApiError("SSO_UNAVAILABLE",error instanceof CentralPlatformRequestError?error.message:"App sign-in is unavailable."),{status:error instanceof CentralPlatformRequestError?error.status:502});}
}
