import json
import hashlib
import hmac
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.db import IntegrityError
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.tenants.policies import tenant_missing_required_policy
from apps.tenants.policies import tenant_demo_block_reason
from apps.tenants.models import Module, Tenant

from .models import AppConnector, ConnectorEvent, ConnectorHealthLog, ConnectorRequestNonce


def _allowed_connector_secrets():
    active = str(getattr(settings, "CONNECTOR_SHARED_SECRET", "") or "")
    nxt = str(getattr(settings, "CONNECTOR_SHARED_SECRET_NEXT", "") or "")
    allow = [("active", active)] if active else []
    if nxt:
        allow.append(("next", nxt))
    return allow


def _connector_authorized(request):
    expected = _allowed_connector_secrets()
    provided = request.headers.get("X-Connector-Secret", "")
    for version, sec in expected:
        if provided == sec:
            return True, version
    return False, ""


def _extract_request_security(request):
    timestamp_raw = request.headers.get("X-Connector-Timestamp", "").strip()
    signature = request.headers.get("X-Connector-Signature", "").strip()
    nonce = request.headers.get("X-Connector-Nonce", "").strip()
    require_signed = bool(getattr(settings, "CONNECTOR_REQUIRE_SIGNED_REQUESTS", False))
    has_signed_headers = bool(timestamp_raw and signature)

    if not require_signed and not has_signed_headers:
        return True, "", None, signature, False, nonce, "unsigned"

    if not timestamp_raw or not signature:
        return False, "Missing signature headers.", None, signature, False, nonce, ""
    if not nonce:
        return False, "Missing connector nonce header.", None, signature, True, nonce, ""

    try:
        ts_int = int(timestamp_raw)
    except ValueError:
        return False, "Invalid connector timestamp header.", None, signature, False, nonce, ""

    source_timestamp = datetime.fromtimestamp(ts_int, tz=dt_timezone.utc)
    max_skew = int(getattr(settings, "CONNECTOR_SIGNATURE_MAX_SKEW_SECONDS", 300))
    age = abs((timezone.now() - source_timestamp).total_seconds())
    if age > max_skew:
        return (
            False,
            "Connector request timestamp is outside allowed skew.",
            source_timestamp,
            signature,
            False,
            nonce,
            "",
        )

    payload = request.body or b""
    signed = f"{timestamp_raw}.{nonce}.".encode("utf-8") + payload
    is_valid = False
    matched_version = ""
    for version, sec in _allowed_connector_secrets():
        expected_sig = hmac.new(sec.encode("utf-8"), signed, hashlib.sha256).hexdigest()
        if hmac.compare_digest(signature, expected_sig):
            is_valid = True
            matched_version = version
            break
    if not is_valid:
        return (
            False,
            "Connector signature verification failed.",
            source_timestamp,
            signature,
            True,
            nonce,
            "",
        )

    return True, "", source_timestamp, signature, True, nonce, matched_version


def _reserve_nonce(*, event_type, module, tenant, nonce, source_timestamp, request_signature):
    if not nonce:
        return True, ""
    try:
        with transaction.atomic():
            ConnectorRequestNonce.objects.create(
                nonce=nonce,
                event_type=event_type,
                module=module,
                tenant=tenant,
                source_timestamp=source_timestamp,
                request_signature=request_signature,
            )
        return True, ""
    except IntegrityError:
        return False, "Connector request replay detected (nonce already used)."


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8")) if request.body else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Invalid JSON payload")


def _extract_event_identity(request, payload):
    external_event_id = (
        request.headers.get("X-External-Event-Id", "").strip()
        or str(payload.get("external_event_id", "")).strip()
        or str(payload.get("event_id", "")).strip()
    )
    idempotency_key = (
        request.headers.get("X-Idempotency-Key", "").strip()
        or str(payload.get("idempotency_key", "")).strip()
    )
    return external_event_id, idempotency_key


def _duplicate_event(event_type, module, tenant, external_event_id, idempotency_key):
    base = ConnectorEvent.objects.filter(event_type=event_type, module=module, tenant=tenant)
    if external_event_id:
        hit = base.filter(external_event_id=external_event_id).order_by("-id").first()
        if hit:
            return hit
    if idempotency_key:
        hit = base.filter(idempotency_key=idempotency_key).order_by("-id").first()
        if hit:
            return hit
    return None


def _payload_version_valid(request, payload):
    accepted = str(getattr(settings, "API_VERSION", "") or "").strip()
    header_version = str(request.headers.get("X-API-Version", "") or "").strip()
    payload_version = str(payload.get("api_version", "") or "").strip()
    supplied = header_version or payload_version
    if not accepted or not supplied:
        return True, ""
    if supplied != accepted:
        return False, f"Unsupported API version '{supplied}'. Expected '{accepted}'."
    return True, ""


def _validate_payload_shape(event_type, payload):
    rules = {
        "tenant.sync": {"tenant_code", "module_code"},
        "usage.report": {"module_code"},
        "webhook.event": {"event_name"},
    }
    required = rules.get(event_type, set())
    missing = [key for key in required if not payload.get(key)]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, ""


def _health_log(endpoint, status_code, is_success, reason="", module=None, tenant=None, auth_key_version=""):
    ConnectorHealthLog.objects.create(
        endpoint=endpoint,
        status_code=int(status_code),
        is_success=bool(is_success),
        auth_key_version=(auth_key_version or "")[:20],
        reason=(reason or "")[:255],
        module=module,
        tenant=tenant,
    )


@require_http_methods(["GET"])
def connector_health(request):
    failure_count = ConnectorHealthLog.objects.filter(is_success=False).count()
    recent_failures = ConnectorHealthLog.objects.filter(is_success=False).order_by("-created_at")[:5]
    return JsonResponse(
        {
            "status": "ok",
            "service": "central-platform-connectors",
            "recent_failure_count": failure_count,
            "recent_failures": [
                {"endpoint": row.endpoint, "status_code": row.status_code, "reason": row.reason}
                for row in recent_failures
            ],
        }
    )


@require_http_methods(["GET"])
def connector_api_docs(request):
    context = {
        "api_version": str(getattr(settings, "API_VERSION", "unknown")),
        "rate_limit_window": int(getattr(settings, "API_RATE_LIMIT_WINDOW_SECONDS", 60)),
        "connector_rate_limit": int(getattr(settings, "API_RATE_LIMIT_CONNECTOR_REQUESTS", 300)),
        "general_rate_limit": int(getattr(settings, "API_RATE_LIMIT_REQUESTS", 120)),
        "deprecation_date": str(getattr(settings, "API_DEPRECATION_DATE", "") or ""),
    }
    return render(request, "connectors/api_docs.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def tenant_sync(request):
    authorized, secret_version = _connector_authorized(request)
    if not authorized:
        _health_log("tenant.sync", 403, False, "Connector authorization failed")
        return JsonResponse({"detail": "Connector authorization failed."}, status=403)
    sig_ok, sig_detail, source_timestamp, request_signature, signed_headers, nonce, auth_key_version = _extract_request_security(
        request
    )
    if not sig_ok:
        _health_log("tenant.sync", 403, False, sig_detail, auth_key_version=secret_version)
        return JsonResponse({"detail": sig_detail}, status=403)
    try:
        payload = _json_body(request)
    except ValueError:
        _health_log("tenant.sync", 400, False, "Invalid JSON payload", auth_key_version=secret_version)
        return HttpResponseBadRequest("Invalid JSON payload")
    valid_ver, ver_detail = _payload_version_valid(request, payload)
    if not valid_ver:
        _health_log("tenant.sync", 400, False, ver_detail, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": ver_detail}, status=400)
    shape_ok, shape_detail = _validate_payload_shape("tenant.sync", payload)
    if not shape_ok:
        _health_log("tenant.sync", 400, False, shape_detail, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": shape_detail}, status=400)

    tenant_code = payload.get("tenant_code")
    module_code = payload.get("module_code")
    status = payload.get("status", "active")
    if not tenant_code or not module_code:
        _health_log("tenant.sync", 400, False, "tenant_code/module_code required", auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": "tenant_code and module_code are required."}, status=400)

    try:
        tenant = Tenant.objects.get(tenant_code=tenant_code)
    except Tenant.DoesNotExist:
        _health_log("tenant.sync", 404, False, "tenant not found", auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": "tenant not found."}, status=404)
    demo_issue = tenant_demo_block_reason(tenant)
    if demo_issue:
        _health_log("tenant.sync", 409, False, demo_issue, tenant=tenant, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": demo_issue}, status=409)
    try:
        module = Module.objects.get(code=module_code)
    except Module.DoesNotExist:
        _health_log("tenant.sync", 404, False, "module not found", auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": "module not found."}, status=404)

    external_event_id, idempotency_key = _extract_event_identity(request, payload)
    duplicate = _duplicate_event(
        "tenant.sync",
        module=module,
        tenant=tenant,
        external_event_id=external_event_id,
        idempotency_key=idempotency_key,
    )
    if duplicate:
        return JsonResponse(
            {"accepted": True, "duplicate": True, "event_id": duplicate.id},
            status=200,
        )
    nonce_ok, nonce_detail = _reserve_nonce(
        event_type="tenant.sync",
        module=module,
        tenant=tenant,
        nonce=nonce,
        source_timestamp=source_timestamp,
        request_signature=request_signature,
    )
    if not nonce_ok:
        _health_log("tenant.sync", 409, False, nonce_detail, module=module, tenant=tenant, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": nonce_detail}, status=409)

    ConnectorEvent.objects.create(
        event_type="tenant.sync",
        module=module,
        tenant=tenant,
        payload=payload,
        external_event_id=external_event_id,
        idempotency_key=idempotency_key,
        request_signature=request_signature,
        signature_valid=signed_headers,
        auth_key_version=auth_key_version or secret_version,
        source_timestamp=source_timestamp,
        status=status,
    )
    connector, _ = AppConnector.objects.get_or_create(module=module, tenant=tenant)
    connector.last_seen_at = timezone.now()
    connector.save(update_fields=["last_seen_at", "updated_at"])
    _health_log("tenant.sync", 200, True, module=module, tenant=tenant, auth_key_version=auth_key_version or secret_version)
    return JsonResponse({"accepted": True, "tenant_id": tenant.id, "module_id": module.id})


@csrf_exempt
@require_http_methods(["POST"])
def usage_report(request):
    authorized, secret_version = _connector_authorized(request)
    if not authorized:
        _health_log("usage.report", 403, False, "Connector authorization failed")
        return JsonResponse({"detail": "Connector authorization failed."}, status=403)
    sig_ok, sig_detail, source_timestamp, request_signature, signed_headers, nonce, auth_key_version = _extract_request_security(
        request
    )
    if not sig_ok:
        _health_log("usage.report", 403, False, sig_detail, auth_key_version=secret_version)
        return JsonResponse({"detail": sig_detail}, status=403)
    try:
        payload = _json_body(request)
    except ValueError:
        _health_log("usage.report", 400, False, "Invalid JSON payload", auth_key_version=secret_version)
        return HttpResponseBadRequest("Invalid JSON payload")
    valid_ver, ver_detail = _payload_version_valid(request, payload)
    if not valid_ver:
        _health_log("usage.report", 400, False, ver_detail, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": ver_detail}, status=400)
    shape_ok, shape_detail = _validate_payload_shape("usage.report", payload)
    if not shape_ok:
        _health_log("usage.report", 400, False, shape_detail, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": shape_detail}, status=400)

    module = None
    tenant = None
    module_code = payload.get("module_code")
    tenant_code = payload.get("tenant_code")
    if module_code:
        module = Module.objects.filter(code=module_code).first()
    if tenant_code:
        tenant = Tenant.objects.filter(tenant_code=tenant_code).first()
    if tenant:
        demo_issue = tenant_demo_block_reason(tenant)
        if demo_issue:
            _health_log("usage.report", 409, False, demo_issue, module=module, tenant=tenant, auth_key_version=auth_key_version or secret_version)
            return JsonResponse({"detail": demo_issue}, status=409)

    external_event_id, idempotency_key = _extract_event_identity(request, payload)
    duplicate = _duplicate_event(
        "usage.report",
        module=module,
        tenant=tenant,
        external_event_id=external_event_id,
        idempotency_key=idempotency_key,
    )
    if duplicate:
        return JsonResponse(
            {"accepted": True, "duplicate": True, "event_id": duplicate.id},
            status=200,
        )
    nonce_ok, nonce_detail = _reserve_nonce(
        event_type="usage.report",
        module=module,
        tenant=tenant,
        nonce=nonce,
        source_timestamp=source_timestamp,
        request_signature=request_signature,
    )
    if not nonce_ok:
        _health_log("usage.report", 409, False, nonce_detail, module=module, tenant=tenant, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": nonce_detail}, status=409)

    ConnectorEvent.objects.create(
        event_type="usage.report",
        module=module,
        tenant=tenant,
        payload=payload,
        external_event_id=external_event_id,
        idempotency_key=idempotency_key,
        request_signature=request_signature,
        signature_valid=signed_headers,
        auth_key_version=auth_key_version or secret_version,
        source_timestamp=source_timestamp,
        status="accepted",
    )
    _health_log("usage.report", 200, True, module=module, tenant=tenant, auth_key_version=auth_key_version or secret_version)
    return JsonResponse({"accepted": True})


@csrf_exempt
@require_http_methods(["POST"])
def webhook_events(request):
    authorized, secret_version = _connector_authorized(request)
    if not authorized:
        _health_log("webhook.event", 403, False, "Connector authorization failed")
        return JsonResponse({"detail": "Connector authorization failed."}, status=403)
    sig_ok, sig_detail, source_timestamp, request_signature, signed_headers, nonce, auth_key_version = _extract_request_security(
        request
    )
    if not sig_ok:
        _health_log("webhook.event", 403, False, sig_detail, auth_key_version=secret_version)
        return JsonResponse({"detail": sig_detail}, status=403)
    try:
        payload = _json_body(request)
    except ValueError:
        _health_log("webhook.event", 400, False, "Invalid JSON payload", auth_key_version=secret_version)
        return HttpResponseBadRequest("Invalid JSON payload")
    valid_ver, ver_detail = _payload_version_valid(request, payload)
    if not valid_ver:
        _health_log("webhook.event", 400, False, ver_detail, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": ver_detail}, status=400)
    shape_ok, shape_detail = _validate_payload_shape("webhook.event", payload)
    if not shape_ok:
        _health_log("webhook.event", 400, False, shape_detail, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": shape_detail}, status=400)

    module_code = payload.get("module_code")
    tenant_code = payload.get("tenant_code")
    event_name = str(payload.get("event_name", "")).strip().lower()
    module = Module.objects.filter(code=module_code).first() if module_code else None
    tenant = Tenant.objects.filter(tenant_code=tenant_code).first() if tenant_code else None
    if tenant:
        demo_issue = tenant_demo_block_reason(tenant)
        if demo_issue:
            _health_log("webhook.event", 409, False, demo_issue, module=module, tenant=tenant, auth_key_version=auth_key_version or secret_version)
            return JsonResponse({"detail": demo_issue}, status=409)

    external_event_id, idempotency_key = _extract_event_identity(request, payload)
    duplicate = _duplicate_event(
        "webhook.event",
        module=module,
        tenant=tenant,
        external_event_id=external_event_id,
        idempotency_key=idempotency_key,
    )
    if duplicate:
        return JsonResponse(
            {"accepted": True, "duplicate": True, "event_id": duplicate.id},
            status=200,
        )
    nonce_ok, nonce_detail = _reserve_nonce(
        event_type="webhook.event",
        module=module,
        tenant=tenant,
        nonce=nonce,
        source_timestamp=source_timestamp,
        request_signature=request_signature,
    )
    if not nonce_ok:
        _health_log("webhook.event", 409, False, nonce_detail, module=module, tenant=tenant, auth_key_version=auth_key_version or secret_version)
        return JsonResponse({"detail": nonce_detail}, status=409)

    if tenant and event_name.startswith("booking."):
        missing = tenant_missing_required_policy(tenant, "marketplace")
        if missing:
            _health_log(
                "webhook.event",
                409,
                False,
                "Required marketplace agreements are missing.",
                module=module,
                tenant=tenant,
                auth_key_version=auth_key_version or secret_version,
            )
            return JsonResponse(
                {
                    "accepted": False,
                    "detail": "Required marketplace agreements are missing.",
                    "missing_agreements": missing,
                },
                status=409,
            )

    try:
        with transaction.atomic():
            from .lifecycle import apply_provider_update
            apply_provider_update(payload, tenant, module)
            from .inventory import apply_inventory
            apply_inventory(payload, tenant, module)
            ConnectorEvent.objects.create(
                event_type="webhook.event",
                module=module,
                tenant=tenant,
                payload=payload,
                external_event_id=external_event_id,
                idempotency_key=idempotency_key,
                request_signature=request_signature,
                signature_valid=signed_headers,
                auth_key_version=auth_key_version or secret_version,
                source_timestamp=source_timestamp,
                status="accepted",
            )
    except ValueError as exc:
        return JsonResponse({"accepted": False, "detail": str(exc)}, status=422)
    _health_log("webhook.event", 200, True, module=module, tenant=tenant, auth_key_version=auth_key_version or secret_version)
    return JsonResponse({"accepted": True})
