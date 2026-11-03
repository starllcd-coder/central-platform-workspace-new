import json
from urllib.parse import urlencode
from django.conf import settings
from django.core import signing
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.paymentsvc.models import CentralPayment, PaymentStatus
from apps.paymentsvc.services import create_payment, verify_and_finalize
from .models import MarketplaceBooking

@csrf_exempt
@require_POST
def start_checkout(request):
    try:
        body=json.loads(request.body)
        data=signing.loads(str(body.get("token") or ""),salt="marketplace-confirmation-v1",max_age=86400)
    except (ValueError,TypeError,AttributeError,signing.BadSignature):return JsonResponse({"detail":"A valid confirmation link is required."},status=401)
    mode=getattr(settings,"PAYMENT_GATEWAY_MODE","disabled")
    if mode=="disabled":return JsonResponse({"detail":"Online payment is not enabled."},status=503)
    with transaction.atomic():
        booking=MarketplaceBooking.objects.select_for_update().select_related("tenant","module").filter(booking_id=data.get("booking_id")).first()
        if not booking:return JsonResponse({"detail":"Booking not found."},status=404)
        if booking.status in {"failed","cancelled","completed"}:return JsonResponse({"detail":"This booking is not payable."},status=409)
        if booking.payment_status=="paid":return JsonResponse({"status":"paid","charged":False})
        if mode=="mock":return JsonResponse({"testMode":True,"charged":False,"status":"simulated","message":"Test checkout only. No money was collected."})
        if booking.fulfillment_status!="provider_confirmed":return JsonResponse({"detail":"Waiting for provider confirmation before payment."},status=409)
        origin=settings.NEXIVO_PUBLIC_URL.rstrip("/")
        if not origin.startswith("https://"):return JsonResponse({"detail":"A secure checkout return URL is required."},status=503)
        url=origin+"/booking-confirmation?"+urlencode({"token":body["token"]})
        latest=CentralPayment.objects.filter(booking_id=booking.booking_id).order_by("-id").first()
        attempt=CentralPayment.objects.filter(booking_id=booking.booking_id).count()+1 if latest and latest.transaction_status in {"failed","cancelled","expired"} else max(1,CentralPayment.objects.filter(booking_id=booking.booking_id).count())
        try:
            payment,_=create_payment({"tenant_id":booking.tenant_id,"module_code":booking.module.code,"booking_id":booking.booking_id,
                "amount":str(booking.total_amount),"currency":booking.currency,"payment_method":"card","booking_type":"online",
                "idempotency_key":booking.booking_id+f":checkout:{attempt}","metadata":{"success_url":url,"cancel_url":url,
                    "customer_email":booking.customer_email,"description":f"Nexivo {booking.booking_id}"}})
            return JsonResponse({"checkoutUrl":payment.metadata.get("checkout_url"),"paymentId":payment.payment_id,"status":payment.transaction_status})
        except (ValueError,KeyError) as exc:return JsonResponse({"detail":str(exc)},status=503)

@csrf_exempt
@require_POST
def check_checkout(request):
    try:
        data=json.loads(request.body)
        claims=signing.loads(str(data.get("token") or ""),salt="marketplace-confirmation-v1",max_age=86400)
        payment=CentralPayment.objects.filter(booking_id=claims["booking_id"]).order_by("-id").first()
        if not payment:return JsonResponse({"status":"unpaid"})
        if payment.transaction_status in {PaymentStatus.PENDING,PaymentStatus.CREATED}:
            payment=verify_and_finalize(payment)
        return JsonResponse({"status":payment.transaction_status})
    except (ValueError,TypeError,KeyError,signing.BadSignature):return JsonResponse({"detail":"Payment verification is unavailable."},status=400)
