import hashlib
import json
from decimal import Decimal,InvalidOperation
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import PaymentDelivery
from .payment_provider import apply_payment

@csrf_exempt
@require_POST
def payment_update(request):
    from apps.orders.central_connector import verify_central_request
    valid,error=verify_central_request(request)
    error="" if valid else error
    if error:return JsonResponse({"ok":False,"error":error},status=403)
    try:
        data=json.loads(request.body)
        if data.get("tenant_code")!=settings.CENTRAL_TENANT_CODE or data.get("module_code")!=settings.CENTRAL_MODULE_CODE:raise ValueError("Tenant or module mismatch.")
        event_id=str(data.get("external_event_id") or "")
        if not event_id or len(event_id)>120:raise ValueError("A valid payment event ID is required.")
        digest=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
        amount=Decimal(str(data.get("amount") or "0"))
        if not amount.is_finite() or amount<=0 or data.get("kind") not in {"payment","refund"}:raise ValueError("Invalid payment amount or kind.")
        with transaction.atomic():
            receipt,created=PaymentDelivery.objects.get_or_create(event_id=event_id,defaults={"payload_hash":digest})
            if receipt.payload_hash!=digest:raise ValueError("Payment event ID already used with different content.")
            if created:apply_payment(data,amount)
        return JsonResponse({"ok":True,"duplicate":not created})
    except (ValueError,TypeError,InvalidOperation,AttributeError) as exc:return JsonResponse({"ok":False,"error":str(exc)},status=409)
