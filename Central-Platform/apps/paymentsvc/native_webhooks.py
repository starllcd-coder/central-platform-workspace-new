import hashlib
import hmac
import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import GatewayConfig, CentralPayment
from .services import handle_webhook, build_adapter

@csrf_exempt
@require_POST
def stripe_native(request):
    config=GatewayConfig.objects.filter(provider="stripe",is_enabled=True).first()
    secret=config.get_webhook_secret() if config else ""
    entries=[part.split("=",1) for part in request.headers.get("Stripe-Signature","").split(",") if "=" in part]
    try:
        ts=next(value for key,value in entries if key=="t")
        expected=hmac.new(secret.encode(),ts.encode()+b"."+request.body,hashlib.sha256).hexdigest()
        valid=secret and abs(time.time()-int(ts))<=300 and any(key=="v1" and hmac.compare_digest(value,expected) for key,value in entries)
        if not valid:return JsonResponse({"detail":"Invalid Stripe signature."},status=403)
        event=json.loads(request.body)
        if event.get("type") not in {"checkout.session.completed","checkout.session.async_payment_succeeded","checkout.session.expired","checkout.session.async_payment_failed"}:
            return JsonResponse({"received":True,"ignored":True})
        obj=event["data"]["object"]
        payload={"event_id":event["id"],"payment_ref":obj["id"],"status":"paid" if obj.get("payment_status")=="paid" else "pending"}
        log=handle_webhook("stripe",payload,signature_valid=True)
        return JsonResponse({"received":True,"status":log.processing_status},status=503 if log.processing_status=="failed" else 200)
    except (ValueError,TypeError,KeyError,StopIteration):return JsonResponse({"detail":"Invalid Stripe event."},status=400)

@csrf_exempt
@require_POST
def thawani_native(request):
    config=GatewayConfig.objects.filter(provider="thawani",is_enabled=True).first()
    # Configured callback URL includes this secret. Payment truth always comes from the authenticated session API.
    secret=config.get_webhook_secret() if config else ""
    if not secret or not hmac.compare_digest(request.GET.get("token",""),secret):return JsonResponse({"detail":"Unauthorized callback."},status=403)
    try:
        event=json.loads(request.body)
        data=event.get("data",event)
        ref=str(data.get("session_id") or data.get("id") or "")
        payment=CentralPayment.objects.filter(gateway_name="thawani",external_reference=ref).first()
        if not payment:return JsonResponse({"received":True,"ignored":True})
        checked=build_adapter("thawani").verify_payment(external_reference=ref)
        log=handle_webhook("thawani",{"event_id":f"{ref}:{checked['status']}","payment_ref":ref,"status":checked["status"]},signature_valid=True)
        return JsonResponse({"received":True,"status":log.processing_status},status=503 if log.processing_status=="failed" else 200)
    except (ValueError,TypeError,KeyError):return JsonResponse({"detail":"Callback verification unavailable."},status=503)
