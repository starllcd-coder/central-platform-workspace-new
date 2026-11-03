import json
import hashlib
import hmac
import uuid
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.connectors.models import ConnectorEvent
from apps.ops.services import log_audit, queue_notification
from apps.marketplace.models import MarketplaceBooking, CustomerTokenVersion
from apps.stay.models import StayBooking
from apps.tenants.models import DemoTenantRequest, MarketplaceListing, Module, Tenant, TenantModule


TOKEN_SALT = "marketplace-customer-v1"
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 14


def _nexivo_lead_authorized(request):
    timestamp = request.headers.get("X-Nexivo-Timestamp", "").strip()
    reference = request.headers.get("X-Idempotency-Key", "").strip()
    signature = request.headers.get("X-Nexivo-Signature", "").strip()
    secret = str(getattr(settings, "NEXIVO_LEAD_SHARED_SECRET", "") or "")
    if not timestamp or not reference or not signature or not secret:
        return False, "Missing Nexivo lead signature headers.", ""
    if len(reference) > 120:
        return False, "Invalid Nexivo lead reference.", ""
    try:
        timestamp_value = int(timestamp)
    except ValueError:
        return False, "Invalid Nexivo lead timestamp.", ""
    max_skew = int(getattr(settings, "NEXIVO_LEAD_SIGNATURE_MAX_SKEW_SECONDS", 300))
    if abs(int(timezone.now().timestamp()) - timestamp_value) > max_skew:
        return False, "Nexivo lead timestamp is outside allowed skew.", ""
    signed = f"{timestamp}.{reference}.".encode("utf-8") + (request.body or b"")
    expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return False, "Nexivo lead signature verification failed.", ""
    return True, "", reference


def _demo_request_payload(payload):
    fields = {
        "business_name": str(payload.get("businessName") or "").strip(),
        "owner_name": str(payload.get("fullName") or "").strip(),
        "owner_email": str(payload.get("email") or "").strip().lower(),
        "owner_phone": str(payload.get("phone") or "").strip(),
        "country": str(payload.get("country") or "").strip().upper(),
        "city": str(payload.get("city") or "").strip(),
        "product_interest": str(payload.get("productInterest") or "").strip().lower(),
        "business_type": str(payload.get("businessType") or "").strip(),
        "estimated_size": str(payload.get("estimatedSize") or "").strip(),
        "message": str(payload.get("message") or "").strip(),
    }
    required = [
        "business_name",
        "owner_name",
        "owner_email",
        "owner_phone",
        "country",
        "city",
        "product_interest",
        "business_type",
        "estimated_size",
    ]
    missing = [name for name in required if not fields[name]]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    try:
        validate_email(fields["owner_email"])
    except ValidationError as exc:
        raise ValueError("Enter a valid business email address.") from exc
    valid_interests = dict(DemoTenantRequest.PRODUCT_INTEREST_CHOICES)
    if fields["product_interest"] not in valid_interests:
        raise ValueError("Unsupported product interest.")
    return fields


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8")) if request.body else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Invalid JSON payload")


def _authenticate_email(request, email, password):
    users = get_user_model().objects.filter(email__iexact=email, is_active=True)
    if users.count() != 1:
        return None
    return authenticate(request, username=users.first().get_username(), password=password)


def _issue_token(user_id, email, mfa=False):
    version = CustomerTokenVersion.objects.filter(user_id=user_id).values_list("version", flat=True).first() or 0
    payload = {"uid": int(user_id), "email": str(email or "").lower(), "version": version, "mfa": mfa, "mfa_at": timezone.now().timestamp() if mfa else 0}
    return signing.dumps(payload, salt=TOKEN_SALT)


def _extract_bearer_token(request):
    raw = (request.headers.get("Authorization", "") or "").strip()
    if not raw.lower().startswith("bearer "):
        return ""
    return raw.split(" ", 1)[1].strip()


def _auth_customer(request):
    token = _extract_bearer_token(request)
    if not token:
        return None
    try:
        claims = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
    except Exception:
        return None
    user_id = claims.get("uid")
    email = (claims.get("email") or "").strip().lower()
    if not user_id:
        return None
    User = get_user_model()
    user = User.objects.filter(id=user_id, email__iexact=email, is_active=True).first()
    version = CustomerTokenVersion.objects.filter(user_id=user_id).values_list("version", flat=True).first() or 0
    if claims.get("version", 0) != version:
        return None
    request.marketplace_claims = claims
    return user


def _tenant_payload(tenant):
    return {
        "id": tenant.id,
        "tenant_code": tenant.tenant_code,
        "name": tenant.name,
        "slug": slugify(tenant.name) or tenant.tenant_code.lower(),
        "module_type": tenant.module_type,
        "country": tenant.country,
        "currency": tenant.currency,
        "status": tenant.status,
    }


def _marketplace_booking_payload(row):
    return {
        "bookingId": row.booking_id,
        "confirmationToken": signing.dumps({"booking_id": row.booking_id}, salt="marketplace-confirmation-v1"),
        "tenantName": row.tenant.name,
        "tenantCode": row.tenant.tenant_code,
        "moduleCode": row.module.code,
        "moduleName": row.module.name,
        "status": row.status,
        "fulfillmentStatus": row.fulfillment_status,
        "paymentStatus": row.payment_status,
        "amount": str(row.total_amount),
        "currency": row.currency,
        "createdAt": row.created_at.isoformat(),
    }


@require_http_methods(["GET"])
def api_health(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "central-platform-marketplace-api",
            "server_time": timezone.now().isoformat(),
        }
    )


@require_http_methods(["GET"])
def tenants_api(request):
    enabled_tenant_ids = TenantModule.objects.filter(marketplace_enabled=True, enabled=True).values_list(
        "tenant_id", flat=True
    )
    tenants = Tenant.objects.filter(id__in=enabled_tenant_ids, status__in=["active", "trial"]).order_by("name")
    return JsonResponse({"results": [_tenant_payload(t) for t in tenants]})


@require_http_methods(["GET"])
def listings_api(request):
    module_code = (request.GET.get("module") or "").strip().lower()
    search_text = (request.GET.get("q") or "").strip()
    from .quotes import public_listings
    rows = public_listings().select_related("tenant__branding").filter(provider_resource_id__gt="")
    if module_code:
        rows = rows.filter(module__code__iexact=module_code)
    if search_text:
        rows = rows.filter(
            Q(tenant__name__icontains=search_text)
            | Q(tenant__country__icontains=search_text)
            | Q(module__name__icontains=search_text)
        )

    try:
        offset=max(0,int(request.GET.get("offset","0")))
        limit=min(500,max(1,int(request.GET.get("limit","500"))))
    except ValueError:
        return JsonResponse({"detail":"Invalid inventory pagination."},status=400)
    total=rows.count()
    results = []
    for row in rows.order_by("pk")[offset:offset+limit]:
        branding = getattr(row.tenant, "branding", None)
        results.append(
            {
                "id": row.id,
                "listing_slug": row.public_slug,
                "tenant_id": row.tenant_id,
                "tenant_code": row.tenant.tenant_code,
                "tenant_name": row.tenant.name,
                "tenant_country": row.tenant.country,
                "image_url": branding.logo_url if branding else "",
                "module_code": row.module.code,
                "module_name": row.module.name,
                "provider_resource_id": row.provider_resource_id,
                "provider_resource_name": row.provider_resource_name,
                "provider_resource_unit": row.provider_resource_unit,
                "base_price": str(row.base_price),
                "average_rating": str(row.average_rating),
                "rating_count": row.rating_count,
                "resource": row.snapshot,
                "currency": row.tenant.currency,
            }
        )
    return JsonResponse({"results": results,"count":total,"nextOffset":offset+limit if offset+limit<total else None})


@require_http_methods(["GET"])
def search_api(request):
    destination = (request.GET.get("destination") or request.GET.get("q") or "").strip()
    module = (request.GET.get("category") or request.GET.get("module") or "").strip().lower()
    from .quotes import public_listings
    rows = public_listings().filter(provider_resource_id__gt="")
    if destination:
        rows = rows.filter(Q(tenant__name__icontains=destination) | Q(tenant__country__icontains=destination))
    if module and module != "all":
        rows = rows.filter(module__code__iexact=module)
    data = []
    for row in rows[:200]:
        data.append(
            {
                "id": row.id,
                "title": f"{row.tenant.name} - {row.module.name}",
                "tenantCode": row.tenant.tenant_code,
                "moduleCode": row.module.code,
                "priceFrom": str(row.base_price),
                "currency": row.tenant.currency,
                "rating": str(row.average_rating),
            }
        )
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")

    full_name = str(payload.get("fullName") or payload.get("name") or "").strip()
    email = str(payload.get("email") or "").strip().lower()
    password = str(payload.get("password") or "")
    if not email or not password:
        return JsonResponse({"detail": "email and password are required."}, status=400)

    User = get_user_model()
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({"detail": "email already registered."}, status=409)

    username = email
    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name[:150],
        )
    token = _issue_token(user.id, user.email)
    return JsonResponse(
        {
            "accessToken": token,
            "refreshToken": "",
            "user": {"id": str(user.id), "name": full_name or user.username, "email": user.email},
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")

    email = str(payload.get("email") or "").strip().lower()
    password = str(payload.get("password") or "")
    if not email or not password:
        return JsonResponse({"detail": "email and password are required."}, status=400)

    user = _authenticate_email(request, email, password)
    if user is None:
        return JsonResponse({"detail": "Invalid credentials."}, status=401)
    token = _issue_token(user.id, user.email)
    display_name = ((user.first_name or "") + " " + (user.last_name or "")).strip() or user.username
    return JsonResponse(
        {
            "accessToken": token,
            "refreshToken": "",
            "user": {"id": str(user.id), "name": display_name, "email": user.email},
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def submit_booking_api(request):
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")

    if payload.get("paymentMethod") == "pay-online" and getattr(settings, "PAYMENT_GATEWAY_MODE", "disabled") == "disabled":
        return JsonResponse({"detail": "Online checkout is not configured yet. Choose an available pay-later option."}, status=503)

    listing_slug = str(payload.get("listingSlug") or payload.get("listing_slug") or "").strip()
    customer_name = str(payload.get("fullName") or payload.get("customer_name") or "").strip()
    customer_email = str(payload.get("email") or payload.get("customer_email") or "").strip().lower()
    customer_phone = str(payload.get("phone") or payload.get("customer_phone") or "").strip()
    idempotency_key = (
        request.headers.get("X-Idempotency-Key", "").strip()
        or str(payload.get("idempotency_key") or payload.get("idempotencyKey") or "").strip()
    )
    if not listing_slug:
        return JsonResponse({"detail": "listingSlug is required."}, status=400)

    from .quotes import get_listing
    try:
        match = get_listing(listing_slug)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    provider_resource_id = str(
        match.provider_resource_id
        or payload.get("providerResourceId")
        or payload.get("vehicleId")
        or payload.get("roomId")
        or payload.get("serviceId")
        or ""
    ).strip()
    if not provider_resource_id:
        return JsonResponse({"detail": "This listing has no provider resource configured."}, status=422)

    if match.module.code == "staylux":
        start_date = parse_date(str(payload.get("checkIn") or payload.get("check_in") or ""))
        end_date = parse_date(str(payload.get("checkOut") or payload.get("check_out") or ""))
        if not start_date or not end_date or end_date <= start_date:
            return JsonResponse({"detail": "Valid checkIn and checkOut are required."}, status=422)
    elif match.module.code == "drivesphere":
        start_date = parse_date(str(payload.get("pickupDate") or payload.get("pickup_date") or ""))
        end_date = parse_date(str(payload.get("returnDate") or payload.get("return_date") or ""))
        if not start_date or not end_date or end_date <= start_date:
            return JsonResponse({"detail": "Valid pickupDate and returnDate are required."}, status=422)
    else:
        start_date = parse_date(str(payload.get("pickupDate") or payload.get("pickup_date") or ""))
        end_date = None
        if not start_date:
            return JsonResponse({"detail": "pickupDate is required."}, status=422)

    if idempotency_key:
        existing = MarketplaceBooking.objects.filter(
            idempotency_key=idempotency_key,
            tenant=match.tenant,
            module=match.module,
        ).first()
        if existing:
            from .quotes import selection
            if existing.listing_id != match.pk or selection(existing.payload) != selection(payload) or existing.customer_email != customer_email:
                return JsonResponse({"detail":"Booking request key was already used for different details."},status=409)
            response = _marketplace_booking_payload(existing)
            response["duplicate"] = True
            return JsonResponse(response)


    from .quotes import calculate, verify_quote
    from apps.connectors.client import ProviderUnavailable
    try:
        quoted = calculate(match, payload)
        total_amount = Decimal(quoted["amount"])
        verify_quote(match, payload, total_amount, quoted)
    except ProviderUnavailable as exc:
        return JsonResponse({"detail": str(exc)}, status=503)
    except (ValueError, TypeError, InvalidOperation, KeyError) as exc:
        return JsonResponse({"detail": str(exc)}, status=422)


    booking_ref = f"NXV-{timezone.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    marketplace_status = "pending"
    fulfillment_status = "connector_queued"
    payment_status = "test_unpaid" if payload.get("paymentMethod") == "pay-online" and getattr(settings,"PAYMENT_GATEWAY_MODE","disabled")=="mock" else "unpaid"
    stay_booking = None

    with transaction.atomic():
        match = MarketplaceListing.objects.select_for_update().get(pk=match.pk)
        if idempotency_key:
            concurrent = MarketplaceBooking.objects.filter(tenant=match.tenant,module=match.module,idempotency_key=idempotency_key).first()
            if concurrent:
                response = _marketplace_booking_payload(concurrent)
                response["duplicate"] = True
                return JsonResponse(response)
        if match.module.code == "staylux":
            unit_filter = {"status": "active"}
            if provider_resource_id.isdigit():
                unit_filter["id"] = int(provider_resource_id)
            else:
                unit_filter["code__iexact"] = provider_resource_id
            unit = match.tenant.units.filter(**unit_filter).first()
            if unit:
                stay_booking = StayBooking.objects.create(
                    tenant=match.tenant,
                    module=match.module,
                    unit=unit,
                    booking_id=booking_ref,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    check_in=start_date,
                    check_out=end_date,
                    guests=max(int(payload.get("guests") or 1), 1),
                    status="pending",
                    payment_rule="pay_now",
                    payment_status="unpaid",
                    currency=match.tenant.currency or "OMR",
                    subtotal_amount=total_amount,
                    total_amount=total_amount,
                    notes=str(payload.get("notes") or "").strip(),
                )
                booking_ref = stay_booking.booking_id
                marketplace_status = "confirmed"
                fulfillment_status = "central_confirmed"

        event = ConnectorEvent.objects.create(
            event_type="webhook.event",
            module=match.module,
            tenant=match.tenant,
            payload={
                "event_name": "booking.requested" if match.module.code != "laundrex" else "order.requested",
                "booking_id": booking_ref,
                "module_code": match.module.code,
                "tenant_code": match.tenant.tenant_code,
                "source": "nexivo",
                "provider_resource_id": provider_resource_id,
                "total_amount": str(total_amount),
                "currency": match.tenant.currency or "OMR",
                "payload": payload,
            },
            external_event_id=booking_ref,
            idempotency_key=idempotency_key,
            status="accepted",
        )

        marketplace_booking = MarketplaceBooking.objects.create(
            booking_id=booking_ref,
            listing=match,
            tenant=match.tenant,
            module=match.module,
            connector_event=event,
            stay_booking=stay_booking,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            status=marketplace_status,
            fulfillment_status=fulfillment_status,
            payment_status=payment_status,
            currency=match.tenant.currency or "OMR",
            subtotal_amount=total_amount,
            total_amount=total_amount,
            payload=payload,
            idempotency_key=idempotency_key,
        )

    return JsonResponse(_marketplace_booking_payload(marketplace_booking), status=201)


@csrf_exempt
@require_http_methods(["POST"])
def submit_booking_finalize_api(request):
    expected_secret = str(getattr(settings, "MARKETPLACE_FINALIZE_SECRET", "") or "")
    provided_secret = request.headers.get("X-Marketplace-Webhook-Secret", "")
    if not expected_secret or not hmac.compare_digest(provided_secret, expected_secret):
        return JsonResponse({"detail": "Unauthorized."}, status=403)
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")
    booking_id = str(payload.get("bookingId") or payload.get("booking_id") or "").strip()
    if not booking_id:
        return JsonResponse({"detail": "bookingId is required."}, status=400)
    booking = MarketplaceBooking.objects.filter(booking_id=booking_id).first()
    if booking:
        booking.status = "confirmed"
        booking.payment_status = str(payload.get("paymentStatus") or payload.get("payment_status") or booking.payment_status)
        booking.save(update_fields=["status", "payment_status", "updated_at"])
        return JsonResponse(_marketplace_booking_payload(booking))
    return JsonResponse({"detail": "booking not found."}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def payment_session_api(request):
    if getattr(settings,"PAYMENT_GATEWAY_MODE","disabled")=="live":
        from .checkout import start_checkout
        return start_checkout(request)
    if getattr(settings, "PAYMENT_GATEWAY_MODE", "disabled") != "mock":
        return JsonResponse({"detail": "Live checkout requires configured payment gateways."}, status=503)
    try:
        payload = _json_body(request)
        amount = Decimal(str(payload.get("amount", "0")))
        if not amount.is_finite() or amount <= 0:
            raise ValueError("Invalid amount")
    except (ValueError, TypeError, InvalidOperation, AttributeError):
        return JsonResponse({"detail": "A positive finite amount is required."}, status=422)
    return JsonResponse({
        "sessionId": "test_" + uuid.uuid4().hex,
        "status": "simulated",
        "testMode": True,
        "charged": False,
        "amount": str(amount),
        "currency": str(payload.get("currency") or "OMR"),
        "message": "Test checkout only. No money was collected.",
    })


@require_http_methods(["GET"])
def booking_confirmation_api(request):
    try:
        payload = signing.loads(request.GET.get("token", ""), salt="marketplace-confirmation-v1", max_age=86400)
    except signing.SignatureExpired:
        return JsonResponse({"detail": "This confirmation link has expired."}, status=410)
    except (signing.BadSignature, ValueError, TypeError):
        return JsonResponse({"detail": "Invalid confirmation link."}, status=401)
    booking = MarketplaceBooking.objects.select_related("tenant", "module").filter(booking_id=payload.get("booking_id")).first()
    if booking is None:
        return JsonResponse({"detail": "Booking not found."}, status=404)
    # A short-lived read-only capability; never disclose customer contact details.
    return JsonResponse({
        "bookingId": booking.booking_id, "tenantName": booking.tenant.name, "moduleName": booking.module.name,
        "status": booking.status, "fulfillmentStatus": booking.fulfillment_status,
        "paymentMethod": booking.payload.get("paymentMethod", "pay-later"),
        "paymentStatus": booking.payment_status, "amount": str(booking.total_amount), "currency": booking.currency,
    })


@require_http_methods(["GET"])
def customer_profile_api(request):
    user = _auth_customer(request)
    if user is None:
        return JsonResponse({"detail": "Unauthorized."}, status=401)
    display_name = ((user.first_name or "") + " " + (user.last_name or "")).strip() or user.username
    return JsonResponse({"id": str(user.id), "name": display_name, "email": user.email})


@require_http_methods(["GET"])
def customer_bookings_api(request):
    user = _auth_customer(request)
    if user is None:
        return JsonResponse({"detail": "Unauthorized."}, status=401)
    rows = (
        MarketplaceBooking.objects.select_related("tenant", "module")
        .filter(customer_email__iexact=user.email)
        .order_by("-created_at")[:200]
    )
    results = [_marketplace_booking_payload(row) for row in rows]
    return JsonResponse({"results": results})


@require_http_methods(["GET"])
def customer_summary_api(request):
    user = _auth_customer(request)
    if user is None:
        return JsonResponse({"detail": "Unauthorized."}, status=401)
    qs = MarketplaceBooking.objects.filter(customer_email__iexact=user.email)
    return JsonResponse(
        {
            "bookingsCount": qs.count(),
            "pendingCount": qs.filter(status="pending").count(),
            "confirmedCount": qs.filter(status="confirmed").count(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def business_onboarding_api(request):
    authorized, reason, external_reference = _nexivo_lead_authorized(request)
    if not authorized:
        return JsonResponse({"detail": reason}, status=403)
    try:
        payload = _json_body(request)
        fields = _demo_request_payload(payload)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    existing = DemoTenantRequest.objects.filter(
        source="nexivo", external_reference=external_reference
    ).first()
    if existing:
        return JsonResponse(
            {
                "demoRequestId": existing.id,
                "leadReference": external_reference,
                "status": existing.status,
                "duplicate": True,
            }
        )

    direct_module_types = dict(Tenant.MODULE_TYPE_CHOICES)
    module_type = fields["product_interest"] if fields["product_interest"] in direct_module_types else ""
    module = Module.objects.filter(code__iexact=module_type).first() if module_type else None
    currency_by_country = {
        "AE": "AED",
        "BH": "BHD",
        "KW": "KWD",
        "OM": "OMR",
        "QA": "QAR",
        "SA": "SAR",
    }
    notes = "\n".join(
        item
        for item in [
            f"Nexivo city: {fields['city']}",
            f"Business type: {fields['business_type']}",
            f"Estimated size: {fields['estimated_size']}",
            fields["message"],
        ]
        if item
    )

    try:
        with transaction.atomic():
            demo_request = DemoTenantRequest.objects.create(
                source="nexivo",
                external_reference=external_reference,
                business_name=fields["business_name"][:180],
                owner_name=fields["owner_name"][:180],
                owner_email=fields["owner_email"],
                owner_phone=fields["owner_phone"][:50],
                country=fields["country"][:80],
                currency=currency_by_country.get(fields["country"], "OMR"),
                timezone="Asia/Dubai",
                product_interest=fields["product_interest"],
                module_type=module_type,
                requested_duration_days=14,
                request_notes=notes,
                status="requested",
            )
            event = ConnectorEvent.objects.create(
                event_type="webhook.event",
                module=module,
                tenant=None,
                external_event_id=external_reference,
                idempotency_key=external_reference,
                payload={
                    "event_name": "business.onboarding",
                    "source": "nexivo",
                    "demo_request_id": demo_request.id,
                    "payload": payload,
                },
                status="accepted",
            )
    except IntegrityError:
        demo_request = DemoTenantRequest.objects.filter(
            source="nexivo", external_reference=external_reference
        ).first()
        if demo_request:
            return JsonResponse(
                {
                    "demoRequestId": demo_request.id,
                    "leadReference": external_reference,
                    "status": demo_request.status,
                    "duplicate": True,
                }
            )
        raise

    log_audit(
        action="tenant.demo.requested.from_nexivo",
        entity_type="DemoTenantRequest",
        entity_id=demo_request.id,
        metadata={
            "external_reference": external_reference,
            "business_name": demo_request.business_name,
            "product_interest": demo_request.product_interest,
            "connector_event_id": event.id,
        },
    )
    queue_notification(
        channel="in_app",
        recipient="ops",
        subject="Nexivo demo request submitted",
        body=(
            f"Demo request #{demo_request.id} for {demo_request.business_name} "
            f"requires Central approval."
        ),
    )
    return JsonResponse(
        {
            "demoRequestId": demo_request.id,
            "leadReference": external_reference,
            "connectorEventId": event.id,
            "status": "pending_approval",
            "duplicate": False,
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def provider_login_api(request):
    try:
        payload = _json_body(request)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")
    email = str(payload.get("email") or "").strip().lower()
    password = str(payload.get("password") or "")
    if not email or not password:
        return JsonResponse({"detail": "email and password are required."}, status=400)

    user = _authenticate_email(request, email, password)
    from apps.accounts.models import TenantMembership
    if user is None or not user.is_active or (not user.is_staff and not user.is_superuser and not TenantMembership.objects.filter(user=user, status="active").exists()):
        return JsonResponse({"detail": "Invalid provider credentials."}, status=401)

    from apps.accounts.models import UserTwoFactor
    from apps.accounts.twofa import verify_totp
    twofa = UserTwoFactor.objects.filter(user=user,is_enabled=True).first()
    if twofa and not verify_totp(twofa.secret,str(payload.get("otp") or "")):
        return JsonResponse({"detail":"A valid two-factor authentication code is required."},status=401)
    token = _issue_token(user.id, user.email, mfa=bool(twofa))
    role = "admin" if user.is_superuser else "partner"
    return JsonResponse(
        {
            "accessToken": token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.get_username(),
                "role": role,
            },
        }
    )
