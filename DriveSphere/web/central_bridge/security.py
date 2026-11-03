import hashlib
import hmac
import time
from django.conf import settings
from django.db import IntegrityError, transaction
from .models import RequestNonce

def authorize(request):
    secret = str(getattr(settings, "CENTRAL_CONNECTOR_SECRET", "") or "")
    tenant = str(getattr(settings, "CENTRAL_TENANT_CODE", "") or "")
    if not secret or not tenant:
        return "Central connector is not configured."
    if not hmac.compare_digest(request.headers.get("X-Connector-Secret", ""), secret):
        return "Unauthorized."
    if request.headers.get("X-Tenant-Code", "") != tenant:
        return "Tenant mismatch."
    timestamp = request.headers.get("X-Connector-Timestamp", "")
    nonce = request.headers.get("X-Connector-Nonce", "")
    signature = request.headers.get("X-Connector-Signature", "")
    if not timestamp or not nonce or len(nonce) > 128 or not signature:
        return "Missing or invalid signature headers."
    try:
        if abs(int(time.time()) - int(timestamp)) > 300:
            return "Expired connector request."
    except ValueError:
        return "Invalid connector timestamp."
    expected = hmac.new(secret.encode(), f"{timestamp}.{nonce}.".encode() + request.body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return "Invalid connector signature."
    try:
        with transaction.atomic():
            RequestNonce.objects.create(nonce=nonce)
    except IntegrityError:
        return "Connector replay detected."
    return ""
