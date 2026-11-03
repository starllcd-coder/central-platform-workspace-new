import hashlib
import json
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Delivery
from .security import authorize
from .provider import create_booking

@csrf_exempt
@require_POST
def receive_booking(request):
    error = authorize(request)
    if error:
        return JsonResponse({"ok": False, "error": error}, status=403)
    try:
        envelope = json.loads(request.body)
        if not isinstance(envelope, dict) or not isinstance(envelope.get("payload"), dict):
            raise ValueError("A booking envelope and payload are required.")
        external_id = str(envelope.get("booking_id") or "").strip()
        if not external_id or len(external_id) > 80:
            raise ValueError("A valid booking_id is required.")
        if envelope.get("tenant_code") != settings.CENTRAL_TENANT_CODE:
            raise ValueError("Tenant mismatch.")
        if envelope.get("module_code") != settings.CENTRAL_MODULE_CODE:
            raise ValueError("Module mismatch.")
        amount = Decimal(str(envelope.get("total_amount", "0")))
        if not amount.is_finite() or amount <= 0:
            raise ValueError("A positive finite booking total is required.")
        digest = hashlib.sha256(json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        with transaction.atomic():
            delivery, _ = Delivery.objects.get_or_create(external_id=external_id, defaults={"payload_hash": digest})
            delivery = Delivery.objects.select_for_update().get(pk=delivery.pk)
            if delivery.payload_hash != digest:
                return JsonResponse({"ok": False, "error": "Booking ID already used with different content."}, status=409)
            if delivery.booking_id:
                return JsonResponse({"ok": True, "duplicate": True, "booking_id": delivery.booking_id})
            booking = create_booking(envelope, amount)
            delivery.booking_id = booking.pk
            delivery.save(update_fields=["booking_id"])
        return JsonResponse({"ok": True, "booking_id": booking.pk}, status=201)
    except (ValueError, TypeError, InvalidOperation, ValidationError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=422)
