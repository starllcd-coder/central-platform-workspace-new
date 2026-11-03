"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
export function CheckoutActions({ token, fulfillment, payment, method }: { token: string; fulfillment: string; payment: string; method: string }) {
  const router=useRouter();const [message,setMessage]=useState("");const [pending,setPending]=useState(false);
  useEffect(()=>{
    if (["paid","refunded"].includes(payment)) return;
    const timer=setInterval(()=>router.refresh(),10000);
    return ()=>clearInterval(timer);
  },[router,payment]);
  useEffect(()=>{
    if (method!=="pay-online" || payment==="paid" || payment==="test_unpaid")return;
    fetch("/api/checkout/status",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token})}).then(()=>router.refresh()).catch(()=>{});
  },[token,method,payment,router]);
  async function pay(){
    setPending(true);setMessage("");
    try{
      const response=await fetch("/api/checkout/start",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token})});
      const result=await response.json();
      if (!response.ok)throw new Error(result.error?.message || "Checkout is unavailable.");
      if(result.data.testMode){setMessage("Test checkout complete. No money was collected.");return;}
      const url=String(result.data.checkoutUrl || "");
      const parsed=new URL(url);
      if(parsed.protocol!=="https:" || !["checkout.stripe.com","checkout.thawani.om","uatcheckout.thawani.om"].includes(parsed.hostname))throw new Error("Invalid checkout destination.");
      window.location.assign(url);
    }catch(error){setMessage(error instanceof Error?error.message:"Checkout is unavailable.");}
    finally{setPending(false);}
  }
  if(method!=="pay-online" || ["paid","refunded"].includes(payment))return null;
  return <div className="space-y-3">
    <Button type="button" variant="luxury" disabled={pending || (fulfillment!=="provider_confirmed" && payment!=="test_unpaid")} onClick={pay}>{pending?"Opening checkout...":"Continue to secure payment"}</Button>
    {fulfillment!=="provider_confirmed" && payment!=="test_unpaid"?<p className="text-sm text-slate-600">Waiting for provider confirmation. This page updates automatically.</p>:null}
    {message?<p role="status" className="text-sm text-slate-600">{message}</p>:null}
  </div>;
}
