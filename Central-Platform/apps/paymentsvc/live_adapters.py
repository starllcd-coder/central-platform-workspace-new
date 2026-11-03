import json
from decimal import Decimal
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

THREE={"OMR","BHD","KWD","JOD","TND"}
ZERO={"JPY","KRW","VND","CLP","XAF","XOF","XPF","RWF","UGX","PYG","GNF","KMF","DJF","BIF","VUV"}

def minor_units(amount,currency):
    multiplier=Decimal(1000 if currency.upper() in THREE else 1 if currency.upper() in ZERO else 100)
    value=Decimal(amount)*multiplier
    if not value.is_finite() or value<=0 or value!=value.to_integral_value():raise ValueError("Amount exceeds the gateway currency precision.")
    return int(value)

def major_units(value,currency):
    return Decimal(str(value))/Decimal(1000 if currency.upper() in THREE else 1 if currency.upper() in ZERO else 100)

class HTTPGateway:
    def __init__(self,config):
        self.config=config
        self.secret=config.get_secret_key()
        if not self.secret:raise ValueError("Gateway credentials are not configured.")
    def request(self,path,body=None,*,key=None):
        headers={"Accept":"application/json",**self.headers}
        if key:headers["Idempotency-Key"]=key
        data=None
        if body is not None:
            if self.form:
                data=urlencode(body).encode();headers["Content-Type"]="application/x-www-form-urlencoded"
            else:
                data=json.dumps(body).encode();headers["Content-Type"]="application/json"
        request=Request(self.base+path,data=data,method="GET" if body is None else "POST",headers=headers)
        try:
            with urlopen(request,timeout=15) as response:payload=json.loads(response.read())
        except (HTTPError,URLError,TimeoutError,OSError) as exc:
            raise ValueError("Gateway request failed. No payment has been confirmed; retry verification before creating another payment.") from exc
        if not isinstance(payload,dict):raise ValueError("Invalid gateway response.")
        return payload

class StripeLiveAdapter(HTTPGateway):
    provider="stripe";base="https://api.stripe.com/v1";form=True
    def __init__(self,config):
        super().__init__(config);self.headers={"Authorization":f"Bearer {self.secret}"}
    def create_payment_session(self,*,payment_id,amount,currency,metadata):
        body={"mode":"payment","client_reference_id":payment_id,"success_url":metadata["success_url"],"cancel_url":metadata["cancel_url"],
            "line_items[0][price_data][currency]":currency.lower(),"line_items[0][price_data][unit_amount]":minor_units(amount,currency),
            "line_items[0][price_data][product_data][name]":metadata.get("description","Nexivo booking"),"line_items[0][quantity]":1,
            "metadata[central_payment_id]":payment_id}
        if metadata.get("card_guarantee"):body["payment_intent_data[capture_method]"]="manual"
        if metadata.get("customer_email"):body["customer_email"]=metadata["customer_email"]
        session=self.request("/checkout/sessions",body,key=payment_id)
        url=str(session.get("url") or "")
        if not url.startswith("https://checkout.stripe.com/"):raise ValueError("Invalid Stripe checkout URL.")
        return {"gateway_payment_ref":session["id"],"checkout_url":url,"status":"pending"}
    def verify_payment(self,*,external_reference):
        session=self.request("/checkout/sessions/"+quote(external_reference,safe=""))
        status="captured" if session.get("payment_status")=="paid" else "expired" if session.get("status")=="expired" else "pending"
        if status=="pending" and session.get("payment_intent"):
            intent=self.request("/payment_intents/"+quote(session["payment_intent"],safe=""))
            if intent.get("status")=="requires_capture":status="authorized"
        return {"status":status,
            "amount":str(major_units(session.get("amount_total",0),session["currency"])),"currency":session["currency"].upper(),
            "reference":session.get("client_reference_id"),"payment_intent":session.get("payment_intent")}
    def get_refund(self,reference):
        result=self.request("/refunds/"+quote(reference,safe=""))
        return {"status":"processed" if result.get("status")=="succeeded" else result.get("status","pending"),
            "amount":str(major_units(result["amount"],result["currency"])),"currency":result["currency"].upper()}
    def refund_payment(self,*,external_reference,amount,reason,idempotency_key):
        session=self.request("/checkout/sessions/"+quote(external_reference,safe=""))
        if not session.get("payment_intent"):raise ValueError("No captured payment intent was found.")
        result=self.request("/refunds",{"payment_intent":session["payment_intent"],"amount":minor_units(amount,session["currency"]),
            "reason":reason if reason in {"duplicate","fraudulent","requested_by_customer"} else "requested_by_customer"},key=idempotency_key)
        return {"refund_reference":result["id"],"status":"processed" if result.get("status")=="succeeded" else result.get("status","pending")}

class ThawaniLiveAdapter(HTTPGateway):
    provider="thawani";form=False
    def __init__(self,config):
        super().__init__(config)
        self.origin=(config.api_base_url or "https://uatcheckout.thawani.om").rstrip("/")
        if self.origin not in {"https://uatcheckout.thawani.om","https://checkout.thawani.om"}:raise ValueError("Use an official Thawani endpoint.")
        if not config.public_key:raise ValueError("Thawani publishable key is required.")
        self.base=self.origin+"/api/v1";self.headers={"thawani-api-key":self.secret}
    def create_payment_session(self,*,payment_id,amount,currency,metadata):
        if currency.upper()!="OMR":raise ValueError("Thawani checkout requires OMR.")
        if metadata.get("card_guarantee"):raise ValueError("Use Stripe for card authorizations; Thawani is configured for payments only.")
        result=self.request("/checkout/session",{"client_reference_id":payment_id,"mode":"payment",
            "products":[{"name":metadata.get("description","Nexivo booking"),"quantity":1,"unit_amount":minor_units(amount,currency)}],
            "success_url":metadata["success_url"],"cancel_url":metadata["cancel_url"],"metadata":{"central_payment_id":payment_id}},key=payment_id)
        if result.get("success") is not True:raise ValueError("Thawani did not create a checkout session.")
        ref=result["data"]["session_id"]
        return {"gateway_payment_ref":ref,"checkout_url":f"{self.origin}/pay/{quote(ref,safe='')}?{urlencode({'key':self.config.public_key})}","status":"pending"}
    def verify_payment(self,*,external_reference):
        result=self.request("/checkout/session/"+quote(external_reference,safe=""))
        if result.get("success") is not True:raise ValueError("Thawani session could not be retrieved.")
        session=result["data"]
        return {"status":"captured" if session.get("payment_status")=="paid" else "pending" if session.get("payment_status")=="unpaid" else "failed",
            "amount":str(Decimal(str(session["total_amount"]))/1000),"currency":"OMR","reference":session.get("client_reference_id"),"invoice":session.get("invoice")}
    def refund_payment(self,*,external_reference,amount,reason,idempotency_key):
        original=self.verify_payment(external_reference=external_reference)
        if original["status"]!="captured" or Decimal(original["amount"])!=amount:
            raise ValueError("Thawani automatic refunds are full-capture refunds only. Use Stripe for partial-refund workflows.")
        invoice=original.get("invoice")
        if not invoice:raise ValueError("The captured Thawani invoice reference is unavailable.")
        result=self.request("/payments?"+urlencode({"checkout_invoice":invoice}))
        rows=result.get("data",[])
        if not isinstance(rows,list):raise ValueError("Thawani payment references could not be verified.")
        matches=[row for row in rows if row.get("payment_id") and Decimal(str(row.get("amount",0)))/1000==amount]
        if len(matches)!=1:raise ValueError("The captured Thawani payment could not be identified uniquely.")
        result=self.request("/refunds",{"payment_id":matches[0]["payment_id"],"reason":reason or "requested_by_customer"},key=idempotency_key)
        if result.get("success") is not True:raise ValueError("Thawani did not acknowledge the refund request.")
        reference=result["data"]["refund_id"]
        checked=self.get_refund(reference)
        if Decimal(checked["amount"])!=amount:raise ValueError("Thawani refund amount needs reconciliation before posting.")
        return {"refund_reference":reference,"status":checked["status"]}
    def get_refund(self,reference):
        result=self.request("/refunds/"+quote(reference,safe=""))
        if result.get("success") is not True:raise ValueError("Thawani refund could not be retrieved.")
        data=result["data"]
        status=str(data.get("refund_status") or data.get("status") or "pending").lower()
        return {"status":"processed" if status in {"succeeded","refunded"} else "failed" if status in {"failed","cancelled"} else "pending",
            "amount":str(Decimal(str(data["amount"]))/1000),"currency":"OMR"}
