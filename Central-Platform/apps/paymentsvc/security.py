import hashlib
import hmac
from datetime import datetime, timezone as dt_timezone
from functools import wraps

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.utils import timezone

from .models import PaymentRequestNonce


def _payment_secrets():
    secrets = []
    active = str(getattr(settings, "PAYMENT_SERVICE_SECRET", "") or "")
    next_secret = str(getattr(settings, "PAYMENT_SERVICE_SECRET_NEXT", "") or "")
    if active:
        secrets.append(("active", active))
    if next_secret:
        secrets.append(("next", next_secret))
    return secrets


def authorize_payment_request(request):
    timestamp_raw = request.headers.get("X-Payment-Timestamp", "").strip()
    nonce = request.headers.get("X-Payment-Nonce", "").strip()
    signature = request.headers.get("X-Payment-Signature", "").strip()
    if not timestamp_raw or not nonce or not signature:
        return False, "Missing payment signature headers.", ""
    if len(nonce) > 120 or len(signature) > 128:
        return False, "Invalid payment signature headers.", ""

    try:
        timestamp_int = int(timestamp_raw)
        source_timestamp = datetime.fromtimestamp(timestamp_int, tz=dt_timezone.utc)
    except (ValueError, OverflowError, OSError):
        return False, "Invalid payment timestamp.", ""

    max_skew = int(getattr(settings, "PAYMENT_SIGNATURE_MAX_SKEW_SECONDS", 300))
    if abs((timezone.now() - source_timestamp).total_seconds()) > max_skew:
        return False, "Payment request timestamp is outside allowed skew.", ""

    full_path = request.get_full_path()
    signed = (
        f"{timestamp_raw}.{nonce}.{request.method.upper()}.{full_path}.".encode("utf-8")
        + (request.body or b"")
    )
    matched_version = ""
    for version, secret in _payment_secrets():
        expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
        if hmac.compare_digest(signature, expected):
            matched_version = version
            break
    if not matched_version:
        return False, "Payment signature verification failed.", ""

    try:
        with transaction.atomic():
            PaymentRequestNonce.objects.create(
                nonce=nonce,
                method=request.method.upper(),
                path=full_path[:255],
                source_timestamp=source_timestamp,
                request_signature=signature,
                auth_key_version=matched_version,
            )
    except IntegrityError:
        return False, "Payment request replay detected.", ""
    return True, "", matched_version


def require_payment_signature(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        valid, reason, key_version = authorize_payment_request(request)
        if not valid:
            return JsonResponse({"detail": reason}, status=403)
        request.payment_auth_key_version = key_version
        return view_func(request, *args, **kwargs)

    return wrapped
