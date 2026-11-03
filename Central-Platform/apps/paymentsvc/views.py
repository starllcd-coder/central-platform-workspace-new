import json
from decimal import Decimal

from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import CentralPayment, GatewayProvider
from .security import require_payment_signature
from .services import (
    create_payment,
    handle_webhook,
    refund_payment,
    verify_and_finalize,
    verify_webhook_signature,
)


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8")) if request.body else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Invalid JSON payload")


def _payment_payload(row: CentralPayment):
    return {
        "payment_id": row.payment_id,
        "booking_id": row.booking_id,
        "parent_booking_id": row.parent_booking_id,
        "gateway_name": row.gateway_name,
        "payment_method": row.payment_method,
        "amount": str(row.amount),
        "currency": row.currency,
        "customer_id": row.customer_id,
        "business_id": row.business_id,
        "transaction_status": row.transaction_status,
        "refund_status": row.refund_status,
        "commission_amount": str(row.commission_amount),
        "business_share": str(row.business_share),
        "checkout_url": row.metadata.get("checkout_url", ""),
        "external_reference": row.external_reference,
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
    }


@csrf_exempt
@require_http_methods(["POST"])
@require_payment_signature
def create_payment_api(request):
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")
    required = ["tenant_id", "amount"]
    for key in required:
        if payload.get(key) in [None, ""]:
            return JsonResponse({"detail": f"{key} is required."}, status=400)
    try:
        row, duplicate = create_payment(payload)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse({"duplicate": duplicate, "payment": _payment_payload(row)}, status=201 if not duplicate else 200)


@csrf_exempt
@require_http_methods(["POST"])
@require_payment_signature
def verify_payment_api(request):
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")
    payment_id = str(payload.get("payment_id") or "").strip()
    if not payment_id:
        return JsonResponse({"detail": "payment_id is required."}, status=400)
    row = CentralPayment.objects.filter(payment_id=payment_id).first()
    if not row:
        return JsonResponse({"detail": "payment not found."}, status=404)
    try:
        row = verify_and_finalize(row)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse({"payment": _payment_payload(row)})


@csrf_exempt
@require_http_methods(["POST"])
@require_payment_signature
def refund_payment_api(request):
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")
    payment_id = str(payload.get("payment_id") or "").strip()
    if not payment_id:
        return JsonResponse({"detail": "payment_id is required."}, status=400)
    row = CentralPayment.objects.filter(payment_id=payment_id).first()
    if not row:
        return JsonResponse({"detail": "payment not found."}, status=404)
    amount = Decimal(str(payload.get("amount") or row.amount))
    reason = str(payload.get("reason") or "")
    try:
        refund, row = refund_payment(row, amount, reason, str(payload.get("idempotency_key") or ""))
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse(
        {
            "refund_id": refund.refund_id,
            "amount": str(refund.amount),
            "status": refund.status,
            "payment": _payment_payload(row),
        },
        status=201,
    )


@require_http_methods(["GET"])
@require_payment_signature
def get_payment_status_api(request):
    payment_id = str(request.GET.get("payment_id") or "").strip()
    if not payment_id:
        return JsonResponse({"detail": "payment_id is required."}, status=400)
    row = CentralPayment.objects.filter(payment_id=payment_id).first()
    if not row:
        return JsonResponse({"detail": "payment not found."}, status=404)
    return JsonResponse({"payment": _payment_payload(row)})


@csrf_exempt
@require_http_methods(["POST"])
@require_payment_signature
def create_card_guarantee_api(request):
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")
    payload["is_card_guarantee"] = True
    try:
        row, duplicate = create_payment(payload)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse({"duplicate": duplicate, "payment": _payment_payload(row)}, status=201 if not duplicate else 200)


@csrf_exempt
@require_http_methods(["POST"])
@require_payment_signature
def process_extension_payment_api(request):
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")
    payload["is_extension_payment"] = True
    try:
        row, duplicate = create_payment(payload)
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse({"duplicate": duplicate, "payment": _payment_payload(row)}, status=201 if not duplicate else 200)


def _webhook_provider(request, provider: str):
    raw = request.body or b""
    try:
        payload = json.loads(raw.decode("utf-8")) if raw else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)
    signature = request.headers.get("X-Gateway-Signature", "")
    timestamp = request.headers.get("X-Gateway-Timestamp", "")
    valid = verify_webhook_signature(provider, raw, signature, timestamp)
    log = handle_webhook(provider, payload, signature_valid=valid)
    response = JsonResponse(
        {
            "received": True,
            "provider": provider,
            "signature_valid": valid,
            "log_id": log.id,
            "processing_status": log.processing_status,
        }
    )
    if not valid:
        response.status_code = 403
    elif log.processing_status == "failed":
        response.status_code = 503
    return response


@csrf_exempt
@require_http_methods(["POST"])
def thawani_webhook(request):
    from django.conf import settings
    if settings.PAYMENT_GATEWAY_MODE == "live":
        from .native_webhooks import thawani_native
        return thawani_native(request)
    return _webhook_provider(request, GatewayProvider.THAWANI)


@csrf_exempt
@require_http_methods(["POST"])
def tap_webhook(request):
    return _webhook_provider(request, GatewayProvider.TAP)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    from django.conf import settings
    if settings.PAYMENT_GATEWAY_MODE == "live":
        from .native_webhooks import stripe_native
        return stripe_native(request)
    return _webhook_provider(request, GatewayProvider.STRIPE)
