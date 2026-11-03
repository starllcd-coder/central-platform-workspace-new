"use client";
import { useEffect,useState } from "react";
export function AppLaunchReturn({ state,tenantCode,moduleCode }: {state:string;tenantCode:string;moduleCode:string}) {
  const [message,setMessage]=useState("Opening your app...");
  useEffect(()=>{
    let cancelled=false;
    fetch("/api/auth/sso-ticket",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({state,tenantCode,moduleCode})})
      .then(async response=>{const result=await response.json();if(!response.ok)throw new Error(result.error?.message || "App sign-in failed.");return result;})
      .then(result=>{if(!cancelled){const url=new URL(result.data.launchUrl);if(!["http:","https:"].includes(url.protocol))throw new Error("Invalid destination.");window.location.replace(url.toString());}})
      .catch(error=>{if(!cancelled)setMessage(error instanceof Error?error.message:"App sign-in failed.");});
    return ()=>{cancelled=true;};
  },[state,tenantCode,moduleCode]);
  return <p role="status" className="text-sm text-slate-600">{message}</p>;
}
