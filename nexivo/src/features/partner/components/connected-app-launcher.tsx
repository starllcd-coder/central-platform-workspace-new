"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
export function ConnectedAppLauncher({ apps }: { apps: { tenantCode:string;moduleCode:string;name:string }[] }) {
  const [message,setMessage]=useState("");const [pending,setPending]=useState(false);
  async function launch(app:{tenantCode:string;moduleCode:string}) {
    setPending(true);setMessage("");
    try{
      const response=await fetch("/api/auth/sso-ticket",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(app)});
      const result=await response.json();
      if(!response.ok)throw new Error(result.error?.message || "App sign-in unavailable.");
      const url=new URL(result.data.beginUrl);
      if(!["http:","https:"].includes(url.protocol))throw new Error("Invalid app URL.");
      window.location.assign(url.toString());
    }catch(error){setMessage(error instanceof Error?error.message:"App sign-in unavailable.");setPending(false);}
  }
  if(!apps.length)return null;
  return <div className="space-y-3"><div className="flex flex-wrap gap-3">{apps.map(app=><Button key={app.tenantCode+app.moduleCode} variant="outline" disabled={pending} onClick={()=>launch(app)}>Open {app.name}</Button>)}</div>{message?<p role="alert" className="text-sm text-slate-600">{message}</p>:null}</div>;
}
